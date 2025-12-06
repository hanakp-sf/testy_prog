"""Graph data model separated from GUI.

Contains class GraphModel: simple in-memory directed graph with vertex
attributes (x,y,label) and edge list.
"""

import os
import subprocess

class GraphModel:
    """Data-only graph model: vertices and directed edges.

    vertices: dict label -> {'x','y','type'}
    edges: list of {'src':src_label, 'dst':dst_label, 'oriented':True|False, 'label':str|None}
    """

    def __init__(self):
        self.repo_dir = None  
        self.vertices = {}
        self.edges = []
        self._next_vid = 1
        # keep numeric counter for fallback/default labels if needed        
        self._commits_metadata = {}  # hash -> {'parents': [hashes]}

    def add_vertex(self, x, y, label, vtype='commit'):
        """Add a vertex keyed by `label`.

        Requirements:
        - `label` must be a non-empty string.
        - labels are unique; if `label` already exists the method returns False.

        On success returns the label (string). On failure returns False.
        """
        if not label or not str(label).strip():
            return False
        label = str(label)
        #already exists
        if label in self.vertices:
            return label
        # add vertex keyed by label
        self.vertices[label] = {'x': x, 'y': y, 'type': vtype}
        # increment the numeric counter for any fallback naming
        self._next_vid += 1
        return label

    def delete_vertex(self, label):
        if label not in self.vertices:
            return
        del self.vertices[label]
        # remove edges referencing this vertex (labels)
        self.edges = [e for e in self.edges if e['src'] != label and e['dst'] != label]

    def move_vertex(self, label, x, y):
        if label in self.vertices:
            self.vertices[label]['x'] = x
            self.vertices[label]['y'] = y

    def add_edge(self, src_label, dst_label, edge_type=True, label=None):
        """Add an edge between vertex labels.

        Returns True on success, False on failure (same endpoints, missing vertices, or duplicate).
        """
        if src_label == dst_label:
            return False
        if src_label not in self.vertices or dst_label not in self.vertices:
            return False
        # check if edge already exists (same direction)
        if any(e['src'] == src_label and e['dst'] == dst_label for e in self.edges):
            return False
        self.edges.append({'src': src_label, 'dst': dst_label, 'oriented': edge_type, 'label': label})
        return True

    def load_branches(self, repo_dir, x0=100, y=60, spacing=150):
        """Load branch names from a local git repository and add them as vertices.

        Positions are laid out horizontally starting at (x0, y).
        Each branch is added with vertex type 'branch', and the tip commit is
        added as a 'commit' vertex directly below, connected with an edge.
        
        If the repo is invalid, returns False.
        """
        # prefer reading refs directly from the repository's .git directory
        if not repo_dir or not os.path.isdir(repo_dir):
            return False

        gitdir = self._resolve_git_dir(repo_dir)
        if not gitdir:
            return False

        self.repo_dir = repo_dir
        try:
            refs = self._read_refs_from_gitdir(gitdir)
        except Exception:
            refs = {}

        branches = list(refs.keys())
        x = x0
        self._branch_tips = getattr(self, '_branch_tips', {})
        
        for b in branches:
            tip = refs.get(b)
            # add branch vertex
            added = self.add_vertex(x, y, b, vtype='branch')
            if tip:
                self._branch_tips[b] = tip
                
            # add tip commit vertex directly below branch (y + 40)
            short_hash = tip[:8]
            commit_label = f'{short_hash}'
            if commit_label not in self.vertices:
                # position commit below branch
                self.add_vertex(x, y + 40, commit_label, vtype='commit')

            # connect branch to tip commit (undirected edge)
            try:
                self.add_edge(b, commit_label, edge_type=False, label=None)
            except Exception:
                pass
            self.load_commit_related(tip, x , y + 40*2)
            x += spacing

        return True

    def _resolve_git_dir(self, repo_dir):
        """Return the path to the .git directory for a working tree.

        Handles the case where .git is a file that points to the real gitdir
        (worktrees or submodules).
        """
        dotgit = os.path.join(repo_dir, '.git')
        if os.path.isdir(dotgit):
            return dotgit
        if os.path.isfile(dotgit):
            try:
                with open(dotgit, 'r', encoding='utf-8') as f:
                    first = f.readline().strip()
                if first.startswith('gitdir:'):
                    path = first.split(':', 1)[1].strip()
                    # path can be relative to repo_dir
                    if not os.path.isabs(path):
                        path = os.path.normpath(os.path.join(repo_dir, path))
                    if os.path.isdir(path):
                        return path
            except Exception:
                return None
        return None

    def _read_refs_from_gitdir(self, gitdir):
        """Read branch refs from the gitdir (refs/heads and packed-refs).

        Returns a dict mapping branch short name -> commit hash.
        """
        refs = {}
        heads_dir = os.path.join(gitdir, 'refs', 'heads')
        # walk refs/heads
        if os.path.isdir(heads_dir):
            for root, _, files in os.walk(heads_dir):
                for fn in files:
                    refpath = os.path.join(root, fn)
                    try:
                        with open(refpath, 'r', encoding='utf-8') as f:
                            h = f.read().strip()
                        # branch name is path relative to heads_dir
                        rel = os.path.relpath(refpath, heads_dir)
                        branch_name = rel.replace(os.sep, '/')
                        if h:
                            refs[branch_name] = h
                    except Exception:
                        continue
        # also read packed-refs
        packed = os.path.join(gitdir, 'packed-refs')
        if os.path.isfile(packed):
            try:
                with open(packed, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or line.startswith('^'):
                            continue
                        parts = line.split()
                        if len(parts) >= 2:
                            h, ref = parts[0], parts[1]
                            if ref.startswith('refs/heads/'):
                                branch_name = ref[len('refs/heads/'):]
                                # prefer refs files over packed-refs (do not override)
                                if branch_name not in refs:
                                    refs[branch_name] = h
            except Exception:
                pass

        return refs

    def load_commit_related(self, commit_hash, x=100, y=60, spacing=150):
        """Load parent commit and tree hashes for a given commit hash.
        Positions are laid out horizontally starting at (x, y).
        Returns True on success, False on failure.
        """
        try:
            proc = subprocess.run(['git', '-C', self.repo_dir, 'cat-file', '-p', commit_hash],
                                  capture_output=True, text=True, check=True)
            out = proc.stdout
        except Exception:
            return False

        parents = []
        tree = None
        #print(out)
        for line in out.splitlines():
            line = line.strip()
            if line.startswith('parent '):
                parts = line.split()
                if len(parts) == 2:
                    parents.append(parts[1])
            elif line.startswith('tree '):
                tree = line.split()[1]
            elif line == '':
                break  # end of headers
   
        # add parent commits as vertices
        xp = x
        for p in parents:
            short_hash = p[:8]
            parent_label = f'{short_hash}'
            if parent_label not in self.vertices:
                self.add_vertex(xp, y + 40, parent_label, vtype='commit')
            # connect commit to parent
            try:
                self.add_edge(parent_label, f'{commit_hash[:8]}', edge_type=True)
            except Exception:
                pass
            xp += spacing
        # add tree as vertex diagonally below commit
        if tree:
            tree_label = f'{tree[:8]}'
            if tree_label not in self.vertices:
                self.add_vertex(x + 20, y + 20, tree_label, vtype='container')
            # connect commit to tree
            try:
                self.add_edge(f'{commit_hash[:8]}', tree_label, label='root', edge_type=False)
            except Exception:
                pass
        return True
