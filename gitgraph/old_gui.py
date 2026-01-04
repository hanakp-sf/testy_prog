import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
from model import GraphModel
import tkinter.font as tkfont
import math, queue, threading, sys, os


from gui_settings import UserSettings

threadresult = False
class GraphGUI(tk.Tk):
    def __init__(self, model=None):
        super().__init__()

        # thread sync queue
        #CC
        self._queue = queue.Queue()

        # render parameters per vertex type: fill color,  outline color and outline width
        #VV
        self.vertex_render_params = {
            'branch': {'fill': "#2EF82E",
                       'color': '',
                       'width': 0
                       },
            'tag': {'fill': "#4622FA",
                       'color': '',
                       'width': 0
                       },
            'commit': {'fill': "#EB55FF",
                       'color': 'black',
                       'width': 2
                       },
            'tree': {'fill': "#FFC90E",
                       'color': 'black',
                       'width': 1
                       },
            'blob': {'fill': "lightgray",
                       'color': 'black',
                       'width': 1
                       },
            'tagobject': {'fill': "lightgray",
                       'color': 'black',
                       'width': 1
                       }
        }
        #VV
        self._init_commit_color = 'pink'

        # GUI types
        #VV
        self.VERTEX = 'rect'
        self.VERTEXLABEL = 'vtext'
        self.EDGE = 'edge'
        self.EDGELABEL = 'etext'

        # Map vertex types to drawing shape functions
        #VV
        self.vertex_render = {
            'branch': self._render_rect_shape,
            'tag': self._render_arrowed_shape,
            'commit': self._render_rounded_shape,
            'tree': self._render_handled_shape,
            'blob': self._render_curved_shape,
            'tagobject': self._render_rounded_shape  
        }

        # Default status message
        #CC
        self.DEFAULT_MESSAGE = (
            "Left-click+drag vertex: move vertex.\n"
            "Right-click vertex: context menu."
        )

        # Widget tags
        # Vertex rectangle: VID (from model), TYPE (from model), VERTEX ( constant)
        # Vertex label: VID (from model), VERTEXLABEL (constant)
        # Edge line: SRC_VID (from model), DEST_VID (from model), EDGE (constant)
        # Edge label: SRC_VID (from model), DEST_VID (from model), EDGELABEL (constant)

        # model injection: use provided model or create a new empty model
        #CC and passed it to VV
        self.model = model if model else GraphModel()
        self._load_model = None

        ## Load settings
        # whether to show tree/blob vertices and edges
        #CC
        self._settings = UserSettings()
        self._settings.load()
        #CC and boolean mirror in VV aby lahko dostupny vo VV pre render
        self._show_trees = tk.BooleanVar(value=self._settings.get_show_tree())
        #CC
        self._current_file = None
        #VV
        self._init_commit = None

        # GUI mappings
        #VV        
        self._drag_data = {'vertex': None, 'x': 0, 'y': 0}
        #CC
        self._user_actions = [] # list of user actions for debugging entry = ('action', 'object_label')

        #CC
        self.geometry("900x600")
        self.minsize(500, 500)

        # ---- Container for scrollable region ----
        #VV
        scrollableFrame = ttk.Frame(self)
        scrollableFrame.pack(fill="both", expand=True)

        # Use grid to make scrollbars align properly
        scrollableFrame.rowconfigure(0, weight=1)
        scrollableFrame.columnconfigure(0, weight=1)

        #CC + canvas to VV
        self.canvas = tk.Canvas(scrollableFrame, bg="white")
        #self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        #VV
        v_scroll = ttk.Scrollbar(scrollableFrame, orient="vertical", command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(scrollableFrame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Update scrollregion
        #VV
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Bindings
        #V
        self._build_bindings()

        # Support for context menu actions
        #VV
        self._context_click = None
        # build menubar and context menu
        #context menus to V, the rest to C
        self.menubar, self.file_menu, self.commit_ctx_menu, self.tree_ctx_menu, self.blob_ctx_menu = self._build_menus()
        self.config(menu=self.menubar)

        #CC
        self.status = tk.Label(self, text=self.DEFAULT_MESSAGE, anchor='w', justify='left')
        self.status.pack(side="bottom", fill=tk.X)

        # trigger function execution on exit
        #CC
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    #context part to V, the rest stay in C
    def _build_menus(self):
        #context menus
        commit_ctx_menu = tk.Menu(self, tearoff=0)
        commit_ctx_menu.add_command(label='Show related', command=self._context_load_commit_connected)
        tree_ctx_menu = tk.Menu(self, tearoff=0)
        tree_ctx_menu.add_command(label='Show tree', command=self._context_show_commit_tree)
        tree_ctx_menu.add_command(label='Hide tree', command=self._context_hide_tree)
        blob_ctx_menu = tk.Menu(self, tearoff=0)
        blob_ctx_menu.add_command(label='Show this path only', command=self._context_show_specific_path)
        # Main menu bar 
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open git folder', command=self._menu_open_folder)
        file_menu.add_separator()
        file_menu.add_command(label='Open diagram file', command=self._menu_open_file)
        file_menu.add_command(label='Save diagram file', command=self._menu_save_file)
        file_menu.add_command(label='Save as', command=self._menu_saveas_file)
        file_menu.add_separator()
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self._menu_exit_app)
        self._update_mru_menu(file_menu)
        menubar.add_cascade(label='File', menu=file_menu)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='Reset filter', command=self._menu_view_reset)
        view_menu.add_command(label='Refresh from Repo', command=self._menu_view_refresh)
        view_menu.add_separator()    
        view_menu.add_checkbutton(label='Show containers', 
                                  onvalue=True, offvalue=False,
                                  variable=self._show_trees,
                                  command=self._toggle_show_trees)
        menubar.add_cascade(label='View', menu=view_menu)
        model_menu = tk.Menu(menubar, tearoff=0)
        model_menu.add_command(label='Model', command=self._menu_print_model)
        model_menu.add_command(label='Actions', command=self._menu_print_actions)
        menubar.add_cascade(label='Print', menu=model_menu)
        return menubar, file_menu, commit_ctx_menu, tree_ctx_menu, blob_ctx_menu

    #V
    def _build_bindings(self):
        # self.bind('<Delete>', self.on_delete_key) disabled delete
        self.canvas.bind('<Button-1>', self.on_left_button_down)
        self.canvas.bind('<B1-Motion>', self.on_left_button_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_left_button_up)
        self.canvas.bind('<Button-3>', self.on_right_button_down)

    #C
    def _update_mru_menu(self, menu):
        last_idx = menu.index('Exit')
        #delete menu items, skip separator
        i = last_idx - 2
        while (menu.type(i) != 'separator'):
            menu.delete(i)
            i -= 1
        last_idx = menu.index('Exit')
        mru_list = self._settings.get_mru_list()
        if len(mru_list) == 0 :
            menu.insert_command(last_idx - 1, label="(No recent files)", state="disabled")
        else:
            for filepath in reversed(mru_list):
                menu.insert_command( last_idx - 1,
                    label=filepath,
                    command=lambda fp=filepath: self.open_file(fp)
                )

    #C
    def update_status_bar(self, message = None, color = 'black'):
        if message is None:
            if len(self.model._filter) > 0:
                self.status.config(text = 'Filter path: ' + self.model.get_filter_as_string(), fg = 'red')
            else:
                self.status.config(text = self.DEFAULT_MESSAGE, fg = color)
        else:
            self.status.config(text = message, fg = color)

    #C
    def update_title(self):
        new_title = '<untitled>'

        if self.model.repo_dir:
            new_title = self.model.repo_dir + ' (' + ('<untitled>' if self._current_file is None else self._current_file) + ')'
        self.title("Git graph for " + new_title)

    # ------------------ Vertex helpers ------------------
    #V
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
    #V
    def _get_vertex_rect(self, label):
        ids = self.canvas.find_withtag( label + ' && ' + self.VERTEX )
        return ids[0] if ids != () else None
    
    # --- label -> canvas_id of vertex label
    #V
    def _get_vertex_text(self, label):
        ids = self.canvas.find_withtag( label + ' && ' + self.VERTEXLABEL )
        return ids[0] if ids != () else None 
    
    # --- (srclabel, dstlabel) -> canvas_id of edge
    #V
    def _get_edge_line(self, srclabel, dstlabel):
        ids = self.canvas.find_withtag( srclabel + ' && ' + dstlabel + ' && ' + self.EDGE )
        return ids[0] if ids != () else None    

    # --- (srclabel, dstlabel) -> canvas_id of edge label
    #V
    def _get_edge_text(self, srclabel, dstlabel):
        ids = self.canvas.find_withtag( srclabel + ' && ' + dstlabel + ' && ' + self.EDGELABEL )
        return ids[0] if ids != () else None 
    
    # --- label -> dimensions of vertex rectangle (rx, ry)
    #V
    def _get_vertex_dimensions(self, label):
        d = self.canvas.bbox(self._get_vertex_rect(label))
        if d == ():
            return d
        return ((d[2]-d[0])/2) - 1, ((d[3]-d[1])/2) - 1  

    #VV
    def _render_rounded_shape(self, label:str, vtype:str, x1:int, y1:int, x2:int, y2:int):
        # some points are repeated to draw direct line instead of curve
        # curves are drawn due to smooth=True
        r = 18
        points = (x1+r, y1, x2-r, y1, x2-r, y1, 
                  x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, 
                  x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, 
                  x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, 
                  x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        rect = self.canvas.create_polygon(points, fill=self._init_commit_color if (vtype == 'commit' and label == self._init_commit) else self.vertex_render_params[vtype]['fill'], 
                            outline=self.vertex_render_params[vtype]['color'], 
                            width=self.vertex_render_params[vtype]['width'], 
                            tags = [label, vtype, self.VERTEX], smooth=True)
        text = self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=label, 
                                       justify = tk.CENTER, tags= [label, vtype, self.VERTEXLABEL])
        
    #VV
    def _render_arrowed_shape(self, label:str, vtype:str, x1:int, y1:int, x2:int, y2:int):
        # constants for arrow rendering
        xd = 6
        yr = (y2 - y1)/2
        points = (x1, y1, x2 - xd, y1, 
                  x2, y1 + yr, x2 - xd, y2,
                  x1, y2, x1 + xd, y1 + yr , x1, y1)
        rect = self.canvas.create_polygon(points, fill=self.vertex_render_params[vtype]['fill'], 
                            outline=self.vertex_render_params[vtype]['color'], 
                            width=self.vertex_render_params[vtype]['width'], 
                            tags = [label, vtype, self.VERTEX])
        text = self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=label, 
                                       justify = tk.CENTER, tags= [label, vtype, self.VERTEXLABEL])
        
    #VV
    def _render_rect_shape(self, label:str, vtype:str, x1:int, y1:int, x2:int, y2:int):
        rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                          fill=self.vertex_render_params[vtype]['fill'],
                                          outline=self.vertex_render_params[vtype]['color'],
                                          width=self.vertex_render_params[vtype]['width'],
                                          tags = [label, vtype , self.VERTEX])
        text = self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=label, justify = tk.CENTER, 
                                       tags= [label, vtype, self.VERTEXLABEL])        

    #VV
    def _render_curved_shape(self, label:str, vtype:str, x1:int, y1:int, x2:int, y2:int):
        # 1/4 of width for curve rendering
        dx = (x2-x1)/4
        # curve constant
        cy = 6
        # make shape higher than standard due to curve
        dy = 3
        y2a = y2 + dy
        y1a = y1 - dy

        points = ( x1, y1a,
            x2, y1a, x2, y1a,
            x2, y2a - cy, x2, y2a - cy,
            x2 - dx, y2a - 2*cy,
            x1 + 2*dx, y2a - cy,
            x1 + dx, y2a,
            x1, y2a - cy, x1, y2a - cy, x1, y1a,  x1, y1a )
        rect = self.canvas.create_polygon(points, fill=self.vertex_render_params[vtype]['fill'], 
                            outline=self.vertex_render_params[vtype]['color'], 
                            width=self.vertex_render_params[vtype]['width'], 
                            tags = [label, vtype, self.VERTEX], smooth=True)
        text = self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2 - dy, text=label, 
                                       justify = tk.CENTER, tags= [label, vtype, self.VERTEXLABEL])

    #VV
    def _render_handled_shape(self, label:str, vtype:str, x1:int, y1:int, x2:int, y2:int):
        # 1/4 of width for curve rendering
        dx = (x2-x1)/3
        # handle constant
        cy = 6
        # make shape higher than standard due to handle
        dy = 6
        y2a = y2 + dy
        y1a = y1 - dy

        points = ( x1 + 2, y1a + cy,
            x2, y1a + cy, x2, y1a + cy,
            x2, y2a, x2, y2a,
            x1, y2a, x1, y2a,
            x1, y1a, x1, y1a,
            x1 + dx - 6 , y1a, x1 + dx - 6 , y1a,
            x1 + dx, y1a,
            x1 + dx, y1a + cy, x1 + dx, y1a + cy, x1 + 2, y1a + cy,x1 + 2, y1a + cy )
        rect = self.canvas.create_polygon(points, fill=self.vertex_render_params[vtype]['fill'], 
                            outline=self.vertex_render_params[vtype]['color'], 
                            width=self.vertex_render_params[vtype]['width'], 
                            tags = [label, vtype, self.VERTEX], smooth=True)
        text = self.canvas.create_text((x1 + x2)/2, (y2a + y1a + cy)/2 , text=label, 
                                       justify = tk.CENTER, tags = [label, vtype, self.VERTEXLABEL])                                       


    #V
    def create_vertex(self, x, y, label=None, vtype=None):
        lbl = label or f"v{self.model._next_vid}"
        text_width, text_height = self._measure_label(lbl)
        paddingx = 10
        paddingy = 10 if vtype in ['branch', 'tag'] else 16
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
        # draw a rectangle vertex (rx, ry are half-width/half-height) using dispatch dictionary
        self.vertex_render[used_type](labelid, used_type, x - rx, y - ry, x + rx, y + ry)
        return labelid

    #V
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

    #V
    def find_vertex_at(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):
            tags = self.canvas.gettags(item)
            # look for VERTEX tag to identify vertex rectangle
            if self.VERTEX in tags:
                return tags[0]  # first tag is the vertex label
        return None

    # ------------------ Edge helpers ------------------
    #V
    def create_edge(self, srclabel, dstlabel, edge_type=True, label=None):
        if not self.model.add_edge(srclabel, dstlabel, edge_type=edge_type, label=label):
            return
        self._create_edge_line(srclabel, dstlabel, edge_type, label)

    #V
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

    #V
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

    #V
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

    #V
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

    # ------------------ Event handlers ------------------
    #V
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

    #V
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

    #V
    def on_left_button_up(self, event):
        vlabel = self._drag_data.get('vertex')
        if vlabel:
            # unhighlight
            try:                    
                self.canvas.itemconfig(self._get_vertex_rect(vlabel), 
                                       outline=self.vertex_render_params[self.model.vertices[vlabel].get('type')]['color'])
            except Exception:
                pass
        self._drag_data['vertex'] = None
        # Update scroll region if drawing expands bounds
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    #V
    def on_right_button_down(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        vlabel = self.find_vertex_at(x, y)
        
        menu_map = {
            'commit': self.commit_ctx_menu,
            'tagobject': self.commit_ctx_menu,
            'tree': self.tree_ctx_menu,
            "blob": self.blob_ctx_menu,
            'branch': None
        }
        ctx_menu = menu_map.get(self.model.vertices[vlabel].get('type'), None) if vlabel else None
        if ctx_menu is not None:
            # show context menu for commit
            self._context_click = (x, y)
            try:
                ctx_menu.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    ctx_menu.grab_release()
                except Exception:
                    pass

    #V
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

    #V
    def _context_load_commit_connected(self):        
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        self._user_actions.append( ('show_commit_related', vlabel) )
        ok = self.model.load_commit_related(vlabel, self.model.vertices[vlabel].get('x'), self.model.vertices[vlabel].get('y') + 40)
        if ok:
            self._render_model()
        self._context_click = None

    #V
    def _context_show_commit_tree(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        self._user_actions.append( ('show_tree', vlabel) )
        ok = self.model.load_tree_contents(vlabel, self.model.vertices[vlabel].get('x'), self.model.vertices[vlabel].get('y') + 60)
        if ok:
            self._render_model()
        self._context_click = None

    #V
    def _context_show_specific_path(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        self.model.build_filter(vlabel)
        self.model.apply_filter()
        self.update_status_bar()
        self._render_model()
        self._context_click = None

    #V
    def _context_hide_tree(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        if vlabel is not None:
            self._user_actions.append( ('hide_tree', vlabel) )
            self.model.hide_tree(vlabel)
            self._render_model()
        self._context_click = None

    #C
    def _menu_open_folder(self):
        """Open a git repository folder and load its branches."""
        try:
            from tkinter import filedialog
            folder = filedialog.askdirectory(title="Select Git repository folder", mustexist=True)
        except Exception:
            folder = None
        if folder:
            self.open_folder(folder)

    #C
    def _menu_save_file(self):
        """Save the current graph model to the file."""
        if self._current_file is None:
            self._menu_saveas_file()
        else:
            try:
                self.model.save_to_file(self._current_file)
            except Exception as e:
                try:
                    messagebox.showerror("Save diagram", f"Error saving diagram to '{self._current_file}': {e}", parent=self)
                except Exception:
                    pass

    #C
    def _menu_saveas_file(self):
        """Save the current graph model to a file."""
        try:
            filepath = filedialog.asksaveasfilename(title="Save diagram file", defaultextension=".ggd",
                                                    filetypes=[("Git Graph Diagram", "*.ggd"), ("All files", "*.*")])
        except Exception:
            filepath = None
        if not filepath:
            return
        try:
            self.model.save_to_file(filepath)
            self._current_file = filepath
            # update mru and menu
            self._settings.add_file(filepath)
            self._update_mru_menu(self.file_menu)
            self.update_title()
        except Exception as e:
            try:
                messagebox.showerror("Save diagram", f"Error saving diagram to '{filepath}': {e}", parent=self)
            except Exception:
                pass

    #C
    def _menu_open_file(self):
        """Open a graph diagram file and load the model."""
        try:
            filepath = filedialog.askopenfilename(title="Open diagram file",
                                                  filetypes=[("Git Graph Diagram", "*.ggd"), ("All files", "*.*")])
        except Exception:
            filepath = None
        if not filepath:
            return
        self.open_file(filepath)

    #C
    def _menu_exit_app(self):
        self._settings.save()
        self.quit()

    #to remove
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

    #C
    def _toggle_show_trees(self):
        #variable is toggled, just render
        self._settings.set_show_tree(self._show_trees.get())
        self._user_actions.append( ('toggle_show_trees', '->' + str(self._show_trees.get())) )
        self._render_model()

    #C
    def _menu_view_reset(self):
        self.model.reset_filter()
        self.model.apply_filter()
        self._render_model()
        self.update_status_bar()

    #C
    def _menu_view_refresh(self):
        global threadresult

        self.menubar.entryconfig('View', state='disabled')
        self.update_status_bar(f'Refreshing ...', 'red')
        threadresult = False
        self.after(100, self.process_queue)
        # trigger model refresh from git folder
        loader = threading.Thread(target=self.refresh_from_folder, daemon=True)
        loader.start()

    #C
    def _menu_print_model(self):
        """Print the current model to the console for debugging."""
        try:
            print("Vertices:")
            for vlabel, v in self.model.vertices.items():
                print(f"  {vlabel}: type='{v.get('type')}', pos=({v.get('x')},{v.get('y')}, visible={v.get('visible')})")
            print("Edges:")
            for e in self.model.edges:
                print(f"  {e}")
        except Exception as e:
            print(f"Error printing model: {e}")

    #C
    def _menu_print_actions(self):
        """Print the list of user actions to the console for debugging."""
        try:
            print("User actions:")
            for action in self._user_actions:
                print(f"  {action}")
        except Exception as e:
            print(f"Error printing actions: {e}")

    #V
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
    
    # C + V split
    def on_new_model(self):
        # clear existing GUI
        self.canvas.delete("all")
        # if init commit is available in model, it will be rendered
        self._init_commit = self.model.init_commit
        self.update_status_bar()
        self.update_title()
        self._render_model()

    #CC
    def on_exit(self):
        self._settings.save()
        self.destroy()

    #C
    def open_file(self, filepath):
        try:
            self.model.load_from_file(filepath)
            self._current_file = filepath
            self.on_new_model()
            # update mru and menu
            self._settings.add_file(filepath)
            self._update_mru_menu(self.file_menu)
        except FileNotFoundError:
            try:
                if messagebox.askyesno(title='File not found', 
                                       message=f'{filepath} was not found. Do you wish to remove it from list ?'):
                    self._settings.remove_file(filepath)
                    self._update_mru_menu(self.file_menu)
            except Exception:
                pass            
        except Exception as e:
            try:
                messagebox.showerror("Open diagram", f"Error loading diagram from '{filepath}': {e}", parent=self)
            except Exception:
                pass

    #C
    def open_folder(self, gitfolder:str):
        if not os.path.isdir(os.path.join(gitfolder, '.git')):
            try:
                messagebox.showerror("Open folder", f"Folder '{gitfolder}' is not a valid Git repository (missing .git).", parent=self)
            except Exception:
                pass
            return
        self.menubar.entryconfig('File', state='disabled')
        self.update_status_bar(f'Loading {gitfolder} ...', 'red')
        self.after(100, self.process_queue)
        # trigger model loading from git folder
        loader = threading.Thread(target=self.load_from_folder, args=(gitfolder,), daemon=True)
        loader.start()

    #C
    def load_from_folder(self, gitfolder:str):
        '''
        Background job to load model from git folder
        '''
        global threadresult

        self._load_model = GraphModel()
        self._load_model.load_refs(gitfolder)
        self._queue.put("LOADEDFOLDER")

    #C
    def refresh_from_folder(self):
        '''
        Background job to refresh model from git folder
        '''    
        global threadresult

        res = self.model.reload_refs()
        threadresult = res
        self._queue.put("REFRESHEDFOLDER")

    #C
    def process_queue(self):
        """Process messages from the background thread."""
        global threadresult

        try:
            message = self._queue.get_nowait()
            if message == 'LOADEDFOLDER':
                # model loaded from git folder
                self.model = self._load_model
                self._load_model = None
                self._current_file = None
                self.on_new_model()
            elif message == 'REFRESHEDFOLDER':
                #model refreshed
                if threadresult:
                    self.on_new_model()
                else:
                    try:
                        messagebox.showerror("Refresh from repo",
                                            f"Error while loading from '{self.model.repo_dir}'. Please, check the path", 
                                            parent=self)
                    except Exception:
                        pass
            self.menubar.entryconfig('File', state='normal')
            self.menubar.entryconfig('View', state='normal')
        except queue.Empty:
            # Continue polling if no message in queue
            self.after(100, self.process_queue)

    # ------------------ Model rendering ------------------
    #V
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
        if not self._show_trees.get():
            for widgedid in list(self.canvas.find_withtag('tree || blob')):
                tags = self.canvas.gettags(widgedid)
                if tags != ():
                    self.delete_vertex(tags[0], False)
        # hide vertices marked as not visible in the model
        for labelid in self.model.vertices:
            if not self.model.vertices[labelid].get('visible', True):
                self.delete_vertex(labelid, False)
        #if init commit updated in model, render it properly
        if self._init_commit != self.model.init_commit:
            self.canvas.itemconfig(self._get_vertex_rect(self.model.init_commit), fill=self._init_commit_color)
            self._init_commit = self.model.init_commit
        # Update scroll region if drawing expands bounds
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    

if __name__ == '__main__':
    startup = 'NOPARAMS'
    # usage: python graph_gui.py <path-to-git-repo>/<diagram-file>
    if len(sys.argv) == 2:
        # check arguments
        param = sys.argv[1]
        startup = 'GITDIR' if os.path.isdir(param) else 'DIAGRAMFILE'
 
    app = GraphGUI(model=GraphModel())
    # render empty model
    app.on_new_model()
    
    # load only branch vertices and tip commits for fast startup
    try:
        if startup == 'GITDIR':
            app.open_folder(param)
        if startup == 'DIAGRAMFILE':
            app.open_file(param)
    except Exception:
        pass
    app.mainloop()

