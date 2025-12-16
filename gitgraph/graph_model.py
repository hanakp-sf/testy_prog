"""Graph data model separated from GUI.

Contains class GraphModel: simple in-memory directed graph with vertex
attributes (x,y,label) and edge list.
"""
import os
import subprocess

class GraphModel:
    """Data-only graph model: vertices and directed edges.

    vertices: dict label -> {'x','y','type', 'visible'}, type in {'commit','branch','tree', 'blob'}, visible is bool
    edges: list of {'src':src_label, 'dst':dst_label, 'oriented':True|False, 'label':str|None, 'path':str|None}
    """

    def __init__(self):
        self.repo_dir = None  
        self.vertices = {}
        self.edges = []
        self._filter = []
        self._next_vid = 1
        # keep numeric counter for fallback/default labels if needed

    def add_vertex(self, x, y, label, vtype='commit'):
        """Add a vertex keyed by `label`.

        Requirements:
        - `label` must be a non-empty string.
        - labels are unique; if `label` already exists the method returns False.
        - type must be one of {'commit','branch','tree','blob'}.

        On success returns the label (string). On failure returns False.
        """
        if not label or not str(label).strip():
            return False
        label = str(label)
        #already exists
        if label in self.vertices:
            return label
        if vtype not in {'commit', 'branch', 'tree', 'blob'}:
            return False
        # add vertex keyed by label
        self.vertices[label] = {'x': x, 'y': y, 'type': vtype, 'visible': True}
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
        self.edges.append({'src': src_label, 'dst': dst_label, 'oriented': edge_type, 'label': label, 'path':None})
        current_edge = self.edges[-1]
        path = self.get_path(dst_label)
        current_edge['path'] = '/' + '/'.join(path[1:]) if len(path) > 0 else None
        # hide destination vertex if not on filter path
        if len(self._filter) > 0 and current_edge['path'] is not None:
            self.vertices[dst_label]['visible'] = self.get_filter_as_string().startswith(current_edge['path'])
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
                self.add_vertex(x + 20, y + 20, tree_label, vtype='tree')
            else:
                # if found make sure it's visible
                self.vertices[tree_label]['visible'] = True
            # connect commit to tree
            try:
                self.add_edge(f'{commit_hash[:8]}', tree_label, label='<ROOT>', edge_type=False)
            except Exception:
                pass
        return True

    def load_tree_contents(self, tree_hash, x=100, y=60, spacing=150):
        """Load the contents of a git tree object given its hash.

        Adds vertices for files and subtrees, positioned starting at (x, y).
        Returns True on success, False on failure.
        """
        try:
            proc = subprocess.run(['git', '-C', self.repo_dir, 'cat-file', '-p',tree_hash],
                                  capture_output=True, text=True, check=True)
            out = proc.stdout
        except Exception:
            return False

        lines = out.splitlines()
        xt = x
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 4:
                mode, type_, obj_hash, name = parts[0], parts[1], parts[2], parts[3]
                short_hash = obj_hash[:8]
                obj_label = f'{short_hash}'
                vtype = type_ if type_ in ['blob', 'tree'] else 'unkown'
                if obj_label not in self.vertices:
                    self.add_vertex(xt, y + 40, obj_label, vtype=vtype)
                else:
                    # if found make sure it's visible
                    self.vertices[obj_label]['visible'] = True
                # connect tree to object
                try:
                    self.add_edge(f'{tree_hash[:8]}', obj_label, label=name, edge_type=False)
                except Exception:
                    pass
                xt += spacing
        return True
    
    def hide_tree(self, tree_hash):
        """Hide the tree vertex and its connected blobs and subtrees."""
        tree_label = f'{tree_hash[:8]}'
        if tree_label in self.vertices:
            self.vertices[tree_label]['visible'] = False
            # hide connected blobs and subtrees
            for e in [item for item in self.edges if item['src'] == tree_label]:
                dst = e['dst']
                if self.vertices[dst]['type'] == 'tree':
                    # recursively hide subtrees
                    self.hide_tree(dst)
                if self.vertices[dst]['type'] == 'blob':
                    # if any blob's parent is visible, keep it visible
                    parents = [item for item in self.edges if item['dst'] == dst]
                    if not any(self.vertices[p['src']]['visible'] for p in parents):
                        self.vertices[dst]['visible'] = False

    def get_path(self, blob_hash):
        if blob_hash not in self.vertices and self.vertices[blob_hash][type] not in ['blob', 'tree']:
            return None
        path = []
        current_vertex = blob_hash
        while (self.vertices[current_vertex]['type'] in ['tree','blob']):
            edges = [item for item in self.edges if item['dst'] == current_vertex]
            path.insert(0, edges[0]['label'])
            current_vertex = edges[0]['src']
        return path

    def build_filter(self, vlabel):
        self._filter = self.get_path(vlabel)

    def reset_filter(self):
        self._filter = []

    def get_filter_as_string(self):
        return '/' + '/'.join(self._filter[1:]) if len(self._filter) > 0 else ''

    def apply_filter(self):
        """Logic
        1. loop all edges with path defined
        2. path of edge is part of filter path, make destination vertex visible, else hide it
        """
        for e in [elem for elem in self.edges if elem['path'] is not None]:
            self.vertices[e['dst']]['visible'] = self.get_filter_as_string().startswith(e['path']) if len(self._filter) > 0 else True


    def save_to_file(self, filepath):
        """Save the graph model to a file in a simple text format.

        global settings are saved as:
        GB repo_dir

        Each vertex is saved as:
        VX label x y type visible

        Each edge is saved as:
        EG src_label dst_label oriented label

        where 'oriented' is 1 for True and 0 for False, and 'label' can be 'None'.
        Exceptions raised are propagated to the caller.
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            # global
            f.write(f"GB {self.repo_dir if self.repo_dir else 'None'}\n")
            # filter
            f.write(f"FT {str(self._filter)}\n")
            # vertices
            for label, attrs in self.vertices.items():
                line = f"VX {label} {int(attrs['x'])} {int(attrs['y'])} {attrs['type']} {int(attrs['visible'])}\n"
                f.write(line)
            # edges
            for e in self.edges:
                oriented = 1 if e['oriented'] else 0
                elabel = e['label'] if e['label'] is not None else 'None'
                line = f"EG {e['src']} {e['dst']} {oriented} {elabel}\n"
                f.write(line)
        
    def load_from_file(self, filepath):
        """Load the graph model from a file in the simple text format.

        Clears existing vertices and edges before loading.
        Exceptions raised are propagated to the caller.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.vertices.clear()
            self.edges.clear()
            self._filter.clear()
            self.repo_dir = None
            for line in f:
                line = line.strip()
                if line.startswith('VX'):
                    parts = line.split()
                    if len(parts) == 6:
                        _, label, x, y, vtype, visible = parts
                        self.vertices[label] = {
                            'x': int(x),
                            'y': int(y),
                            'type': vtype,
                            'visible': bool(int(visible))
                        }
                elif line.startswith('EG'):
                    parts = line.split()
                    if len(parts) == 5:
                        _, src, dst, oriented, elabel = parts
                        oriented_bool = bool(int(oriented))
                        elabel_val = elabel if elabel != 'None' else None
                        self.edges.append({
                            'src': src,
                            'dst': dst,
                            'oriented': oriented_bool,
                            'label': elabel_val,
                            'path': None
                        })
                elif line.startswith('GB'):
                    parts = line.split()
                    if len(parts) == 2:
                        _, dir = parts
                        self.repo_dir = dir if dir != 'None' else None
                elif line.startswith('FT'):
                    parts = line.split()
                    if len(parts) > 1:
                        fl = " ".join(parts[1:])
                        self._filter = eval(fl)
        # calculate path for each edge
        for e in self.edges:
            path = self.get_path(e['dst'])
            e['path'] = '/' + '/'.join(path[1:]) if len(path) > 0 else None
