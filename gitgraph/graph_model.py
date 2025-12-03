"""Graph data model separated from GUI.

Contains class GraphModel: simple in-memory directed graph with vertex
attributes (x,y,rx,ry,label) and edge list.
"""

import os
import subprocess

class GraphModel:
    """Data-only graph model: vertices and directed edges.

    vertices: dict label -> {'x','y','rx','ry','label','type'}
    edges: list of {'src':src_label, 'dst':dst_label, 'oriented':True|False, 'label':str|None}
    """

    def __init__(self):
        self.vertices = {}
        self.edges = []
        self._next_vid = 1
        # keep numeric counter for fallback/default labels if needed        
        self._commits_metadata = {}  # hash -> {'parents': [hashes]}

    def add_vertex(self, x, y, label, rx, ry, vtype='commit'):
        """Add a vertex keyed by `label`.

        Requirements:
        - `label` must be a non-empty string.
        - labels are unique; if `label` already exists the method returns False.

        On success returns the label (string). On failure returns False.
        """
        if not label or not str(label).strip():
            return False
        label = str(label)
        if label in self.vertices:
            return False
        # add vertex keyed by label
        self.vertices[label] = {'x': x, 'y': y, 'rx': rx, 'ry': ry, 'type': vtype}
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

    def load_sample(self):
        """Populate the model with a 5-vertex, 7-edge sample graph.

        This is model-only: positions and simple radii are set here. GUI may
        re-measure labels and adjust rx accordingly when rendering.
        """
        # clear existing
        self.vertices.clear()
        self.edges.clear()
        self._next_vid = 1

        coords = {
            'main': (150, 150),
            'fe78df': (350, 150),
            '89d146': (250, 250),
            'a45b90': (150, 350),
            '5c374f': (350, 350),
        }
        ids = {}
        # default radii
        default_rx = 40
        default_ry = 20
        # assign a variety of types for sample vertices
        sample_types = ['branch', 'commit', 'container', 'file', 'commit']
        for i, (label, (x, y)) in enumerate(coords.items()):
            vtype = sample_types[i % len(sample_types)]
            added = self.add_vertex(x, y, label, default_rx, default_ry, vtype=vtype)
            if added:
                ids[label] = added

        edges = [
            ('main', 'fe78df', False, None),
            ('fe78df', '89d146', True, 'edge3'),
            ('89d146', 'a45b90', True, 'edge4'),
            ('a45b90', 'fe78df', True, 'edge5'),
            ('89d146', '5c374f', True, 'edge6')
        ]
        for s, d, t, lbl in edges:
            # ids store labels, so pass labels directly
            if s in ids and d in ids:
                self.add_edge(s, d, edge_type=t, label=lbl)

    def load_branches(self, repo_dir, x0=100, y=60, spacing=150, rx=60, ry=20):
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
            added = self.add_vertex(x, y, b, rx, ry, vtype='branch')
            if tip:
                self._branch_tips[b] = tip
                
            # add tip commit vertex directly below branch (y + 80)
            short_hash = tip[:8]
            commit_label = f'{short_hash}'
            if commit_label not in self.vertices:
                # position commit below branch
                self.add_vertex(x, y + 80, commit_label, 50, 18, vtype='commit')

            # connect branch to tip commit (undirected edge)
            try:
                self.add_edge(b, commit_label, edge_type=False, label=None)
            except Exception:
                pass
            
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

    def load_commits_for_branch(self, repo_dir, branch, per_branch=20, y_start=140, y_spacing=80, rx=50, ry=18):
        """Lazy-load commits for a single branch on-demand.

        If branch commits are already loaded, returns True without re-loading.
        Returns True on success, False on failure.
        
        Uses _branch_tips[branch] (commit hash) if available for faster rev-list.
        """
        print(f"Loading commits for branch '{branch}'...")
        if not repo_dir or not os.path.isdir(repo_dir):
            return False
        # check if branch position is known
        if branch not in self.vertices:
            return False

        bx = self.vertices[branch]['x']
        # use stored tip hash if available (faster than resolving branch name)
        start_ref = self._branch_tips.get(branch, branch)
        
        # get commits for this branch
        try:
            proc = subprocess.run(['git', '-C', repo_dir, 'rev-list', '--max-count', str(per_branch), start_ref],
                                  capture_output=True, text=True, check=True)
            out = proc.stdout
        except Exception:
            return False

        chashes = [line.strip() for line in out.splitlines() if line.strip()]
        print(chashes)
        # batch-fetch parent info using git cat-file --batch
        parents_map = {}
        if chashes:
            try:
                input_str = '\n'.join(chashes) + '\n'
                proc = subprocess.run(['git', '-C', repo_dir, 'cat-file', '--batch'],
                                      input=input_str, capture_output=True, text=True, check=False)
                out = proc.stdout
                lines = out.splitlines()
                i = 0
                for h in chashes:
                    if i < len(lines):
                        header = lines[i].strip().split()
                        if len(header) >= 2 and header[1] == 'commit':
                            size = int(header[2]) if len(header) > 2 else 0
                            i += 1
                            parents = []
                            while i < len(lines) and lines[i].strip():
                                line = lines[i].strip()
                                if line.startswith('parent '):
                                    parents.append(line.split()[1])
                                i += 1
                            parents_map[h] = parents
                            if i < len(lines) and not lines[i].strip():
                                i += 1
                        else:
                            i += 1
            except Exception:
                # fallback to git log
                try:
                    proc = subprocess.run(['git', '-C', repo_dir, 'log', '--no-walk', '--format=%H%n%P', '--'] + chashes,
                                          capture_output=True, text=True, check=False)
                    out = proc.stdout
                    lines = out.splitlines()
                    for j in range(0, len(lines), 2):
                        if j + 1 < len(lines):
                            hh = lines[j].strip()
                            pp = lines[j+1].strip().split() if lines[j+1].strip() else []
                            parents_map[hh] = pp
                except Exception:
                    pass

        y = y_start
        prev_label = None
        for h in chashes:
            # cache parent info
            if h not in self._commits_metadata and h in parents_map:
                self._commits_metadata[h] = {'parents': parents_map[h]}

            label = f'{h[:8]}'
            if label not in self.vertices:
                added = self.add_vertex(bx, y, label, rx, ry, vtype='commit')
            else:
                added = label

            # connect branch to first commit
            if prev_label is None:
                try:
                    self.add_edge(branch, label, edge_type=True, label=None)
                except Exception:
                    pass

            # connect commit to parent
            parents = self._commits_metadata.get(h, {}).get('parents', [])
            if parents:
                parent = parents[0]
                parent_label = f'{parent[:8]}'
                if parent_label not in self.vertices:
                    self.add_vertex(bx + 40, y + y_spacing/2, parent_label, rx, ry, vtype='commit')
                try:
                    self.add_edge(parent_label, label, edge_type=True, label=None)
                except Exception:
                    pass
            prev_label = label
            y += y_spacing

        return True
