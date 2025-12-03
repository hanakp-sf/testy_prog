import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import tkinter.font as tkfont
import math
import sys
import os

from graph_model import GraphModel


class GraphGUI(tk.Tk):
    def __init__(self, model=None):
        super().__init__()
        self.title("Interactive Directed Graph Creator")
        self.geometry("1280x800")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # colors per vertex type
        self.vertex_colors = {
            'branch': 'lightgreen',
            'commit': 'pink',
            'container': 'lightgray',
            'file': 'khaki'
        }
        # canvas types
        self.RECT = 'rect'
        self.TEXT = 'text'

        # Model and GUI mappings
        self.model = GraphModel()
        self.vertex_by_canvas = {}  # canvas_id -> vid           canvas.gettags(canvas_id)[0]
        self.edges = []  # (src_vid, dst_vid, line_id, label_id)

        self._drag_data = {'vertex': None, 'x': 0, 'y': 0}
        self._repo_dir = None  # set if loading from git repo

        # Bindings
        self.canvas.bind('<Button-1>', self.on_left_button_down)
        self.canvas.bind('<B1-Motion>', self.on_left_button_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_left_button_up)

        self.canvas.bind('<Button-3>', self.on_right_button_down)
        
        # Context menu for canvas (right-click on empty area)
        self._context_click = None
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label='Add vertex...', command=self._context_add_vertex)
        # Menu bar with Vertex submenu
        self.menubar = tk.Menu(self)
        vertex_menu = tk.Menu(self.menubar, tearoff=0)
        vertex_menu.add_command(label='Add vertex...', command=self._menu_add_vertex)
        self.menubar.add_cascade(label='Vertex', menu=vertex_menu)
        model_menu = tk.Menu(self.menubar, tearoff=0)
        model_menu.add_command(label='Print model', command=self._menu_print_model)
        self.menubar.add_cascade(label='Model', menu=model_menu)
        self.config(menu=self.menubar)
        self.bind('<Delete>', self.on_delete_key)

        # Instructions label
        instr = (
            "Left-click+drag vertex: move vertex.\n"
            "Right-click+drag from one vertex to another: create directed edge.\n"
            "Select a vertex and press Delete: remove vertex and connected edges."
        )
        self.status = tk.Label(self, text=instr, anchor='w', justify='left')
        self.status.pack(fill=tk.X)

        # model injection: use provided model or create a new empty model
        if model is None:
            self.model = GraphModel()
        else:
            self.model = model

        # render any existing model state into the GUI
        self._render_model()

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

    # --- vid -> canvas_id of rectangle
    def _get_vertex_rect(self, vid):
        return self.canvas.find_withtag( vid + ' && ' + self.RECT )[0]
    
    # --- vid -> canvas_id of label
    def _get_vertex_text(self, vid):
        return self.canvas.find_withtag( vid + ' && ' + self.TEXT )[0]    
    
    def create_vertex(self, x, y, r=24, label=None, vtype=None):
        lbl = label or f"v{self.model._next_vid}"
        text_width, text_height = self._measure_label(lbl)
        paddingx = 14
        paddingy = 8
        rx = max(r, int(text_width / 2) + paddingx)
        ry = text_height // 2 + paddingy/2

        # pass vertex type to model; default in model is 'commit'
        used_type = vtype if vtype is not None else 'commit'
        vid = self.model.add_vertex(x, y, lbl, rx, ry, vtype=used_type)
        if not vid:
            # failed to add (empty or duplicate label)
            try:
                messagebox.showerror("Vertex label", f"Cannot create vertex. Label '{lbl}' is empty or already exists.", parent=self)
            except Exception:
                pass
            return None
        # draw a rectangle vertex (rx, ry are half-width/half-height)
        # special-case 'branch' vertices: transparent fill and no outline
        if used_type == 'branch':
            fill_color = ''
            outline_color = ''
            outline_width = 0
        else:
            fill_color = self.vertex_colors.get(used_type, 'lightblue')
            outline_color = 'black'
            outline_width = 2
        rect = self.canvas.create_rectangle(x - rx, y - ry, x + rx, y + ry,
                            fill=fill_color, outline=outline_color, width=outline_width, tags = [lbl,  self.RECT])
        text = self.canvas.create_text(x, y, text=lbl, tags= [lbl , self.TEXT])

        self.vertex_by_canvas[rect] = vid
        self.vertex_by_canvas[text] = vid
        return vid

    def delete_vertex(self, vid):
        # remove canvas items
        try:
            self.canvas.delete(self._get_vertex_rect(vid))
        except Exception:
            pass
        try:
            self.canvas.delete(self._get_vertex_text(vid))
        except Exception:
            pass

        # remove edges connected to this vertex (GUI lines)
        new_edges = []
        for edge_info in self.edges:
            s, d, line_id = edge_info[:3]
            label_id = edge_info[3] if len(edge_info) > 3 else None
            if s == vid or d == vid:
                self.canvas.delete(line_id)
                if label_id:
                    self.canvas.delete(label_id)
            else:
                new_edges.append(edge_info)
        self.edges = new_edges

        # cleanup maps
        to_remove = [cid for cid, vv in list(self.vertex_by_canvas.items()) if vv == vid]
        for cid in to_remove:
            del self.vertex_by_canvas[cid]

        # update model
        self.model.delete_vertex(vid)

    def find_vertex_at(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):
            if item in self.vertex_by_canvas:
                print(f"Found vertex at ({x},{y}): canvas item {item}, vid {self.vertex_by_canvas[item]}, tags {self.canvas.gettags(item)}")
                return self.vertex_by_canvas[item]
        return None

    # ------------------ Edge helpers ------------------
    def create_edge(self, src_vid, dst_vid, edge_type=True, label=None):
        if not self.model.add_edge(src_vid, dst_vid, edge_type=edge_type, label=label):
            return
        self._create_edge_line(src_vid, dst_vid, edge_type, label)


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

    # NOTE: rounded-rectangle helpers removed; use ellipse endpoint math below.

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

    def update_edges_for_vertex(self, vid):
        for i, edge_info in enumerate(self.edges):
            s, d, line_id = edge_info[:3]
            label_id = edge_info[3] if len(edge_info) > 3 else None
            if s == vid or d == vid:
                s_v = self.model.vertices[s]
                d_v = self.model.vertices[d]
                x1o, y1o, x2o, y2o = self._rect_line_endpoints(
                    s_v['x'], s_v['y'], s_v['rx'], s_v['ry'], d_v['x'], d_v['y'], d_v['rx'], d_v['ry'])
                self.canvas.coords(line_id, x1o, y1o, x2o, y2o)
                # update label position if it exists
                if label_id:
                    label_x, label_y = self._calculate_label_position(x1o, y1o, x2o, y2o)
                    self.canvas.coords(label_id, label_x, label_y)

    # ------------------ Event handlers ------------------
    def on_left_button_down(self, event):
        x, y = event.x, event.y
        vid = self.find_vertex_at(x, y)
        if vid is None:
            # do not create a new vertex on left-click empty area
            return
        else:
            # trigger lazy loading on first interaction if a branch is clicked
            if self._repo_dir:
                self._trigger_lazy_load(vid)
            # start dragging vertex
            self._drag_data['vertex'] = vid
            self._drag_data['x'] = x
            self._drag_data['y'] = y
            # highlight
            try:
                self.canvas.itemconfig(self._get_vertex_rect(vid), outline='red')
            except Exception:
                pass

    def on_left_button_drag(self, event):
        vid = self._drag_data.get('vertex')
        if not vid:
            return
        dx = event.x - self._drag_data['x']
        dy = event.y - self._drag_data['y']

        # move shapes (rect + text)
        try:
            self.canvas.move(self._get_vertex_rect(vid), dx, dy)
        except Exception:
            pass
        try:
            self.canvas.move(self._get_vertex_text(vid), dx, dy)
        except Exception:
            pass
        # update model position
        m = self.model.vertices[vid]
        m['x'] += dx
        m['y'] += dy
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y
        self.update_edges_for_vertex(vid)

    def on_left_button_up(self, event):
        vid = self._drag_data.get('vertex')
        if vid:
            # unhighlight
            try:
                self.canvas.itemconfig(self._get_vertex_rect(vid), outline='black')
            except Exception:
                pass
        self._drag_data['vertex'] = None

    def on_right_button_down(self, event):
        x, y = event.x, event.y
        vid = self.find_vertex_at(x, y)
        if vid is None:
            # show context menu for adding a vertex at this location
            self._context_click = (x, y)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    self.context_menu.grab_release()
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
        self.create_vertex(x, y, r=24, label=lbl)
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
        self.create_vertex(x, y, r=24, label=lbl)
    
    def _menu_print_model(self):
        """Print the current model to the console for debugging."""
        try:
            print("Vertices:")
            for vid, v in self.model.vertices.items():
                print(f"  {vid}: label='{v.get('label')}', type='{v.get('type')}', pos=({v.get('x')},{v.get('y')})")
            print("Edges:")
            for e in self.model.edges:
                print(f"  {e}")
        except Exception as e:
            print(f"Error printing model: {e}")


    def on_delete_key(self, event):
        # delete currently highlighted vertex (red outline)
        to_delete = None
        for vid in self.model.vertices:
            try:
                cfg = self.canvas.itemcget(self._get_vertex_rect(vid), 'outline')
            except Exception:
                cfg = None
            if cfg == 'red':
                to_delete = vid
                break
        if to_delete:
            self.delete_vertex(to_delete)
    
    def _trigger_lazy_load(self, branch_label):
        """Load commits for a branch on-demand if it's a branch vertex."""
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
        """Render all vertices and edges from the model into the canvas."""
        # clear any existing GUI items
        for vid in self.model.vertices:
            try:
                try:
                    self.canvas.delete(self._get_vertex_rect(vid))
                except Exception:
                    pass
                try:
                    self.canvas.delete(self._get_vertex_text(vid))
                except Exception:
                    pass
            except Exception:
                pass
        for edge_info in list(self.edges):
            _, _, line_id = edge_info[:3]
            label_id = edge_info[3] if len(edge_info) > 3 else None
            try:
                self.canvas.delete(line_id)
                if label_id:
                    self.canvas.delete(label_id)
            except Exception:
                pass
        self.vertex_by_canvas.clear()
        self.edges.clear()

        # create GUI items for vertices using create_vertex
        # collect vertex data first to avoid modifying dict during iteration
        vertex_data = [(vid, v['x'], v['y'], v.get('type', 'commit')) 
                   for vid, v in self.model.vertices.items()]
        # clear model vertices and re-add via create_vertex
        self.model.vertices.clear()
        self.model._next_vid = 1
        for vid, x, y, vtype in vertex_data:
            self.create_vertex(x, y, r=24, label=vid, vtype=vtype)

        # create GUI items for edges (do not add to model — it's already present)
        for edge in self.model.edges:
            src_vid = edge['src']
            dst_vid = edge['dst']
            edge_type = edge.get('oriented', True)
            edge_label = edge.get('label', None)
            self._create_edge_line(src_vid, dst_vid, edge_type, edge_label)

    def _create_edge_line(self, src_vid, dst_vid, edge_type=True, label=None):
        s = self.model.vertices[src_vid]
        d = self.model.vertices[dst_vid]
        x1o, y1o, x2o, y2o = self._rect_line_endpoints(
            s['x'], s['y'], s['rx'], s['ry'], d['x'], d['y'], d['rx'], d['ry'])
        arrow_style = tk.LAST if edge_type else tk.NONE
        line = self.canvas.create_line(x1o, y1o, x2o, y2o, arrow=arrow_style, width=1, fill='black')
        label_id = None
        
        # render label with perpendicular offset if present
        if label:
            try:
                font = tkfont.nametofont("TkDefaultFont")
            except Exception:
                font = tkfont.Font()
            label_x, label_y = self._calculate_label_position(x1o, y1o, x2o, y2o)
            label_id = self.canvas.create_text(label_x, label_y, text=label, font=font, fill='black')
            self.canvas.tag_raise(label_id, line)  # put text in front of line for visibility
        
        self.edges.append((src_vid, dst_vid, line, label_id))


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
    # attach the repo directory on the model for potential future use
    try:
        model.repo_dir = repo_dir
    except Exception:
        pass
    # load only branch vertices, skip commits for fast startup (lazy-load on demand)
    try:
        model.load_branches(repo_dir)
    except Exception:
        pass
    app = GraphGUI(model=model)
    # enable lazy loading: commits will be loaded when user clicks on branch vertices
    app._repo_dir = repo_dir
    app.mainloop()
