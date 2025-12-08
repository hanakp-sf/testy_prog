import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox, ttk
import tkinter.font as tkfont
import math
import sys
import os

from graph_model import GraphModel


class GraphGUI(tk.Tk):
    def __init__(self, model=None):
        super().__init__()

        # colors per vertex type
        self.vertex_colors = {
            'branch': '#ffff00',
            'commit': 'pink',
            'tree': 'lightgray',
            'blob': 'khaki'
        }
        # GUI types
        self.VERTEX = 'rect'
        self.VERTEXLABEL = 'vtext'
        self.EDGE = 'edge'
        self.EDGELABEL = 'etext'

        # Widget tags
        # Vertex rectangle: VID (from model), TYPE (from model), VERTEX ( constant)
        # Vertex label: VID (from model), VERTEXLABEL (constant)
        # Edge line: SRC_VID (from model), DEST_VID (from model), EDGE (constant)
        # Edge label: SRC_VID (from model), DEST_VID (from model), EDGELABEL (constant)

        ##Configuation
        # whether to show tree/blob vertices and edges
        self._show_trees = tk.BooleanVar(value=True) 

        # model injection: use provided model or create a new empty model
        self.model = model if model else GraphModel()
        self._repo_dir = self.model.repo_dir  

        # GUI mappings            
        self._drag_data = {'vertex': None, 'x': 0, 'y': 0}

        self.title("Git graph for " + self._repo_dir if self._repo_dir else "<untitled>")
        self.geometry("900x600")
        self.minsize(500, 500)

        # ---- Container for scrollable region ----
        scrollableFrame = ttk.Frame(self)
        scrollableFrame.pack(fill="both", expand=True)

        # Use grid to make scrollbars align properly
        scrollableFrame.rowconfigure(0, weight=1)
        scrollableFrame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(scrollableFrame, bg="white")
        #self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(scrollableFrame, orient="vertical", command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(scrollableFrame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Update scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Bindings
        self._build_bindings()

        # Support for context menu actions
        self._context_click = None
        # build menubar and context menu
        self.menubar, self.commit_ctx_menu, self.tree_ctx_menu = self._build_menus()
        self.config(menu=self.menubar)

        # Instructions label
        instr = (
            "Left-click+drag vertex: move vertex.\n"
            "Right-click vertex: context menu."
        )
        self.status = tk.Label(self, text=instr, anchor='w', justify='left')
        self.status.pack(side="bottom", fill=tk.X)

        # render any existing model state into the GUI
        self._render_model()

    def _build_menus(self):
        commit_ctx_menu = tk.Menu(self, tearoff=0)
        commit_ctx_menu.add_command(label='Show related', command=self._context_load_commit_connected)
        tree_ctx_menu = tk.Menu(self, tearoff=0)
        tree_ctx_menu.add_command(label='Show tree', command=self._context_show_commit_tree)
        # Menu bar with Vertex submenu
        menubar = tk.Menu(self)
        vertex_menu = tk.Menu(menubar, tearoff=0)
        vertex_menu.add_command(label='Add vertex...', command=self._menu_add_vertex)
        menubar.add_cascade(label='Vertex', menu=vertex_menu)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label='Show containers', 
                                  onvalue=True, offvalue=False,
                                  variable=self._show_trees,
                                  command=self._toggle_show_trees)
        menubar.add_cascade(label='View', menu=view_menu)
        model_menu = tk.Menu(menubar, tearoff=0)
        model_menu.add_command(label='Print model', command=self._menu_print_model)
        menubar.add_cascade(label='Model', menu=model_menu)
        return menubar, commit_ctx_menu, tree_ctx_menu

    def _build_bindings(self):
        # self.bind('<Delete>', self.on_delete_key) disabled delete
        self.canvas.bind('<Button-1>', self.on_left_button_down)
        self.canvas.bind('<B1-Motion>', self.on_left_button_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_left_button_up)
        self.canvas.bind('<Button-3>', self.on_right_button_down)

    # ------------------ Vertex helpers ------------------
    def _measure_label(self, label):
        try:
            font = tkfont.nametofont("TkDefaultFont")
        except Exception:
            font = tkfont.Font()
        # width in pixels
        w = font.measure(label)
        # approximate height in pixels (linespace = ascent+descent)
        try:
            h = font.metrics('linespace') 
        except Exception:
            # fallback estimate
            h = font.metrics('ascent') + font.metrics('descent') if hasattr(font, 'metrics') else int(w * 0.2)
        return w, h

    # --- label -> canvas_id of rectangle
    def _get_vertex_rect(self, label):
        ids = self.canvas.find_withtag( label + ' && ' + self.VERTEX )
        return ids[0] if ids != () else None
    
    # --- label -> canvas_id of vertex label
    def _get_vertex_text(self, label):
        ids = self.canvas.find_withtag( label + ' && ' + self.VERTEXLABEL )
        return ids[0] if ids != () else None 
    
    # --- (srclabel, dstlabel) -> canvas_id of edge
    def _get_edge_line(self, srclabel, dstlabel):
        ids = self.canvas.find_withtag( srclabel + ' && ' + dstlabel + ' && ' + self.EDGE )
        return ids[0] if ids != () else None    

    # --- (srclabel, dstlabel) -> canvas_id of edge label
    def _get_edge_text(self, srclabel, dstlabel):
        ids = self.canvas.find_withtag( srclabel + ' && ' + dstlabel + ' && ' + self.EDGELABEL )
        return ids[0] if ids != () else None 
    
    # --- label -> dimensions of vertex rectangle (rx, ry)
    def _get_vertex_dimensions(self, label):
        d = self.canvas.bbox(self._get_vertex_rect(label))
        if d == ():
            return d
        return ((d[2]-d[0])/2) - 1, ((d[3]-d[1])/2) - 1  
    
    def _create_round_rectangle(self, x1, y1, x2, y2, **kwargs):
        # niektore body sa opakuju na vykreslenie priamych ciar namiesto spline kriviek
        # suvisi to s parametrom smooth=True
        r = 18
        points = (x1+r, y1, x2-r, y1, x2-r, y1, 
                  x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, 
                  x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, 
                  x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, 
                  x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        
        #print (points)
        return self.canvas.create_polygon(points, **kwargs, smooth=True)  

    def create_vertex(self, x, y, label=None, vtype=None):
        lbl = label or f"v{self.model._next_vid}"
        text_width, text_height = self._measure_label(lbl)
        paddingx = 14
        paddingy = 16
        r=24 # minimal half-width
        rx = max(r, int(text_width / 2) + paddingx)
        ry = text_height // 2 + paddingy/2

        # pass vertex type to model; default in model is 'commit'
        used_type = vtype if vtype is not None else 'commit'
        labelid = self.model.add_vertex(x, y, lbl, vtype=used_type)
        if not labelid:
            # failed to add (empty or duplicate label)
            try:
                messagebox.showerror("Vertex label", f"Cannot create vertex. Label '{lbl}' is empty or already exists.", parent=self)
            except Exception:
                pass
            return None
        # draw a rectangle vertex (rx, ry are half-width/half-height)
        # special-case 'branch' vertices: transparent fill and no outline       
        rect = self._create_round_rectangle(x - rx, y - ry, x + rx, y + ry,
                            fill=self.vertex_colors.get(used_type, 'lightblue'), 
                            outline='' if used_type == 'branch' else 'black', 
                            width=0 if used_type == 'branch' else 2, 
                            tags = [lbl, used_type , self.VERTEX])
        text = self.canvas.create_text(x, y, text=lbl, justify = tk.CENTER, tags= [lbl , used_type, self.VERTEXLABEL])
        return labelid

    def delete_vertex(self, label, remove_from_model=True):
        # remove canvas items
        try:
            self.canvas.delete(self._get_vertex_rect(label))
        except Exception:
            pass
        try:
            self.canvas.delete(self._get_vertex_text(label))
        except Exception:
            pass

        # find edges via canvas tags and delete them
        for line_id in self.canvas.find_withtag(self.EDGE + " && " + label):
            s,  d,  _ = self.canvas.gettags(line_id)
            self.canvas.delete(line_id)
            # also delete label if exists
            label_id = self._get_edge_text(s, d)
            if label_id:
                self.canvas.delete(label_id)
        # update model
        if remove_from_model:
            self.model.delete_vertex(label)

    def find_vertex_at(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):
            tags = self.canvas.gettags(item)
            # look for VERTEX tag to identify vertex rectangle
            if self.VERTEX in tags:
                return tags[0]  # first tag is the vertex label
        return None

    # ------------------ Edge helpers ------------------
    def create_edge(self, srclabel, dstlabel, edge_type=True, label=None):
        if not self.model.add_edge(srclabel, dstlabel, edge_type=edge_type, label=label):
            return
        self._create_edge_line(srclabel, dstlabel, edge_type, label)


    def _rect_line_endpoints(self, x1, y1, rx1, ry1, x2, y2, rx2, ry2):
        """Compute line endpoints where the line between centers meets the rectangle borders.

        Rectangles are axis-aligned with half-width rx and half-height ry.
        """
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return x1, y1, x2, y2
        # parametric line: p(t) = (x1,y1) + t*(dx,dy), t in [0,1]
        def intersect_rect(cx, cy, rx, ry, ox, oy):
            # ox, oy are direction components (dx,dy)
            ts = []
            if ox != 0:
                # left/right sides
                t1 = (-rx) / ox
                t2 = (rx) / ox
                ts.extend([t1, t2])
            if oy != 0:
                # top/bottom sides
                t3 = (-ry) / oy
                t4 = (ry) / oy
                ts.extend([t3, t4])
            # convert to absolute t along ray from center to target: we need positive t
            cand = None
            for t in sorted(ts):
                if t <= 0:
                    continue
                px = cx + ox * t
                py = cy + oy * t
                # check if (px,py) lies on rectangle boundary within the other coordinate
                if abs(px - cx) <= rx + 1e-6 and abs(py - cy) <= ry + 1e-6:
                    cand = (px, py)
                    break
            if cand is None:
                return cx, cy
            return cand

        # direction from src to dst
        sx, sy = intersect_rect(x1, y1, rx1, ry1, dx, dy)
        ex, ey = intersect_rect(x2, y2, rx2, ry2, -dx, -dy)
        return sx, sy, ex, ey

    def _calculate_label_position(self, x1, y1, x2, y2, offset=15):
        """Calculate label position perpendicular to edge line.
        
        Args:
            x1, y1: start point of edge
            x2, y2: end point of edge
            offset: distance to offset label from the edge line (pixels)
        
        Returns:
            (label_x, label_y): position for label text
        """
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        
        if dist < 1e-6:  # points are too close
            return mid_x, mid_y
        
        # perpendicular vector (rotated 90 degrees counterclockwise)
        perp_x = -dy / dist
        perp_y = dx / dist
        
        # offset label position
        label_x = mid_x + perp_x * offset
        label_y = mid_y + perp_y * offset
        
        return label_x, label_y

    def update_edges_for_vertex(self, label):
        """Update all edges connected to the given vertex ID."""
        # find edges via canvas tags and update them
        for line_id in self.canvas.find_withtag(self.EDGE + " && " + label):
            s,  d,  _ = self.canvas.gettags(line_id)
            s_v = self.model.vertices[s]
            d_v = self.model.vertices[d]
            srx, sry = self._get_vertex_dimensions(s)
            drx, dry = self._get_vertex_dimensions(d)
            x1o, y1o, x2o, y2o = self._rect_line_endpoints(
                    s_v['x'], s_v['y'], srx, sry, d_v['x'], d_v['y'], drx, dry)                
            self.canvas.coords(line_id, x1o, y1o, x2o, y2o)
            # update label position if it exists
            label_id = self._get_edge_text(s, d)
            if label_id:
                label_x, label_y = self._calculate_label_position(x1o, y1o, x2o, y2o)
                self.canvas.coords(label_id, label_x, label_y)

    # ------------------ Event handlers ------------------
    def on_left_button_down(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        labelid = self.find_vertex_at(x, y)
        if labelid is None:
            # do not create a new vertex on left-click empty area
            return
        else:
            # start dragging vertex
            self._drag_data['vertex'] = labelid
            self._drag_data['x'] = x
            self._drag_data['y'] = y
            # highlight
            try:
                self.canvas.itemconfig(self._get_vertex_rect(labelid), outline='red')
            except Exception:
                pass

    def on_left_button_drag(self, event):
        vlabel = self._drag_data.get('vertex')
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if not vlabel:
            return
        dx = x - self._drag_data['x']
        dy = y - self._drag_data['y']

        # move shapes (rect + text)
        try:
            self.canvas.move(self._get_vertex_rect(vlabel), dx, dy)
        except Exception:
            pass
        try:
            self.canvas.move(self._get_vertex_text(vlabel), dx, dy)
        except Exception:
            pass
        # update model position
        m = self.model.vertices[vlabel]
        m['x'] += dx
        m['y'] += dy
        self._drag_data['x'] = x
        self._drag_data['y'] = y
        self.update_edges_for_vertex(vlabel)

    def on_left_button_up(self, event):
        vlabel = self._drag_data.get('vertex')
        if vlabel:
            # unhighlight
            try:                    
                self.canvas.itemconfig(self._get_vertex_rect(vlabel), 
                                       outline='' if self.model.vertices[vlabel].get('type') == 'branch' else 'black')
            except Exception:
                pass
        self._drag_data['vertex'] = None
        # Update scroll region if drawing expands bounds
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_right_button_down(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        vlabel = self.find_vertex_at(x, y)
        if vlabel and (self.model.vertices[vlabel].get('type') != 'branch'):
            # show context menu for commit
            self._context_click = (x, y)
            if self.model.vertices[vlabel].get('type') == 'commit':
                try:
                    self.commit_ctx_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    try:
                        self.commit_ctx_menu.grab_release()
                    except Exception:
                        pass
            # show context menu for tree
            if self.model.vertices[vlabel].get('type') == 'tree':
                try:
                    self.tree_ctx_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    try:
                        self.tree_ctx_menu.grab_release()
                    except Exception:
                        pass                    
            return

    def _context_add_vertex(self):
        """Create a vertex at the last right-click context position.

        Prompts for an optional label, then creates the vertex.
        """
        if not self._context_click:
            return
        x, y = self._context_click
        # ask for label (can be empty)
        try:
            lbl = simpledialog.askstring("Vertex label", "Label for new vertex (leave empty for default):", parent=self)
        except Exception:
            lbl = None
        # create vertex (create_vertex handles None/empty label)
        self.create_vertex(x, y, label=lbl)
        self._context_click = None

    def _context_load_commit_connected(self):        
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        ok = self.model.load_commit_related(vlabel, self.model.vertices[vlabel].get('x'), self.model.vertices[vlabel].get('y') + 40)
        if ok:
            self._render_model()
        self._context_click = None

    def _context_show_commit_tree(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        ok = self.model.load_tree_contents(vlabel, self.model.vertices[vlabel].get('x'), self.model.vertices[vlabel].get('y') + 60)
        if ok:
            self._render_model()
        self._context_click = None

    def _menu_add_vertex(self):
        """Add a vertex using current pointer location (or canvas center).

        Prompts for a label and creates the vertex at the mouse pointer
        relative to the canvas. If the pointer isn't over the canvas, use
        the canvas center.
        """
        try:
            px = self.winfo_pointerx()
            py = self.winfo_pointery()
            cx = self.canvas.winfo_rootx()
            cy = self.canvas.winfo_rooty()
            x = px - cx
            y = py - cy
        except Exception:
            x = None
            y = None
        # fallback to canvas center
        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
        except Exception:
            w = 200
            h = 200
        if x is None or y is None or x < 0 or y < 0 or x > w or y > h:
            x = w // 2
            y = h // 2
        try:
            lbl = simpledialog.askstring("Vertex label", "Label for new vertex (leave empty for default):", parent=self)
        except Exception:
            lbl = None
        self.create_vertex(x, y, label=lbl)

    def _toggle_show_trees(self):
        """Toggle visibility of tree vertices and edges."""
        self._show_trees = not self._show_trees
        self._render_model()
            
    def _menu_print_model(self):
        """Print the current model to the console for debugging."""
        try:
            print("Vertices:")
            for vlabel, v in self.model.vertices.items():
                print(f"  {vlabel}: type='{v.get('type')}', pos=({v.get('x')},{v.get('y')})")
            print("Edges:")
            for e in self.model.edges:
                print(f"  {e}")
        except Exception as e:
            print(f"Error printing model: {e}")

    def on_delete_key(self, event):
        # delete currently highlighted vertex (red outline)
        to_delete = None
        for vlabel in self.model.vertices:
            try:
                cfg = self.canvas.itemcget(self._get_vertex_rect(vlabel), 'outline')
            except Exception:
                cfg = None
            if cfg == 'red':
                to_delete = vlabel
                break
        if to_delete:
            self.delete_vertex(to_delete)
    
    def _trigger_lazy_load(self, branch_label):
        """Load commits for a branch on-demand if it's a branch vertex."""
        print(f"Triggering lazy load for branch {branch_label} in {self._repo_dir}", )
        if not self._repo_dir:
            return
        v = self.model.vertices.get(branch_label)
        if not v or v.get('type') != 'branch':
            return
        # load commits for this branch
        try:
            ok = self.model.load_commits_for_branch(self._repo_dir, branch_label)
            if ok:
                # re-render the model to display new commits
                self._render_model()
        except Exception:
            pass

    # ------------------ Model rendering ------------------
    def _render_model(self):
        # check if vertex exists in GUI, if not, create it
        for labelid in self.model.vertices:
            rect = self._get_vertex_rect(labelid)           
            if rect is None:
                # skip tree/blob vertices if configured so
                if not self._show_trees and self.model.vertices[labelid].get('type') in ['tree', 'blob']:
                    continue
                v = self.model.vertices[labelid]
                self.create_vertex(v['x'], v['y'], label=labelid, vtype=v.get('type', 'commit'))
        # create edges if not present in GUI
        for edge in self.model.edges:
            s_v = edge['src']
            d_v = edge['dst']
            edge_type = edge.get('oriented', True)
            edge_label = edge.get('label', None)
            # check if edge already exists in GUI
            line_id = self._get_edge_line(s_v, d_v)
            if line_id is None:
                # skip edges connected to tree/blob vertices if configured so
                if not self._show_trees and (self.model.vertices[s_v].get('type') in ['tree', 'blob'] or
                                             self.model.vertices[d_v].get('type') in ['tree', 'blob']):
                    continue
                self._create_edge_line(s_v, d_v, edge_type, edge_label)
        # delete tree/blob vertices and edges if configured so, but do not modify model
        if not self._show_trees:
            for widgedid in list(self.canvas.find_withtag('tree || blob')):
                tags = self.canvas.gettags(widgedid)
                if tags != ():
                    self.delete_vertex(tags[0], False)
        # Update scroll region if drawing expands bounds
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _create_edge_line(self, srclabel, dstlabel, edge_type=True, label=None):
        s = self.model.vertices[srclabel]
        d = self.model.vertices[dstlabel]
        srx, sry = self._get_vertex_dimensions(srclabel)
        drx, dry = self._get_vertex_dimensions(dstlabel)

        x1o, y1o, x2o, y2o = self._rect_line_endpoints(
            s['x'], s['y'], srx, sry, d['x'], d['y'], drx, dry)
        arrow_style = tk.LAST if edge_type else tk.NONE
        line = self.canvas.create_line(x1o, y1o, x2o, y2o, arrow=arrow_style, width=1, fill='black', 
                                       tags=[srclabel, dstlabel, self.EDGE])
        label_id = None
        
        # render label with perpendicular offset if present
        if label:
            try:
                font = tkfont.nametofont("TkDefaultFont")
            except Exception:
                font = tkfont.Font()
            label_x, label_y = self._calculate_label_position(x1o, y1o, x2o, y2o)
            label_id = self.canvas.create_text(label_x, label_y, text=label, font=font, fill='black',
                                               tags=[srclabel, dstlabel, self.EDGELABEL])
            self.canvas.tag_raise(label_id, line)  # put text in front of line for visibility
        

if __name__ == '__main__':
    # usage: python graph_gui.py <path-to-git-repo>
    if len(sys.argv) != 2:
        print("Usage: python graph_gui.py <git-repo-directory>", file=sys.stderr)
        sys.exit(1)
    repo_dir = sys.argv[1]
    if not os.path.isdir(repo_dir):
        print(f"Error: '{repo_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)
    # simple check for a git repo: presence of a .git directory
    if not os.path.isdir(os.path.join(repo_dir, '.git')):
        print(f"Error: '{repo_dir}' does not look like a git repository (missing .git)", file=sys.stderr)
        sys.exit(1)

    model = GraphModel()
    # load only branch vertices, skip commits for fast startup (lazy-load on demand)
    try:
        model.load_branches(repo_dir)
    except Exception:
        pass
    app = GraphGUI(model=model) #when model attached, it is rendered on init
    
    app.mainloop()
