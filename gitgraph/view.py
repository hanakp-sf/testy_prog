import tkinter as tk, math
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
from graph import GraphApp
from model import GraphModel

class GraphView():
    def __init__(self, pController = None , pModel=None):
        # render parameters per vertex type: fill color,  outline color and outline width
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
        
        self._init_commit_color = 'pink'

        # Widget tags
        # Vertex rectangle: VID (from model), TYPE (from model), VERTEX ( constant)
        # Vertex label: VID (from model), VERTEXLABEL (constant)
        # Edge line: SRC_VID (from model), DEST_VID (from model), EDGE (constant)
        # Edge label: SRC_VID (from model), DEST_VID (from model), EDGELABEL (constant)

        # GUI types
        self.VERTEX = 'rect'
        self.VERTEXLABEL = 'vtext'
        self.EDGE = 'edge'
        self.EDGELABEL = 'etext'

        # Map vertex types to drawing shape functions
        self.vertex_render = {
            'branch': self._render_rect_shape,
            'tag': self._render_arrowed_shape,
            'commit': self._render_rounded_shape,
            'tree': self._render_handled_shape,
            'blob': self._render_curved_shape,
            'tagobject': self._render_rounded_shape  
        }

        self.controller = pController if pController  else GraphApp()
        self.model = pModel if pModel else GraphModel()
        self.show_trees = True
        self._init_commit = None
        
        # Support for context menu actions
        self._context_click = None

        # GUI mappings       
        self._drag_data = {'vertex': None, 'x': 0, 'y': 0}

        # ---- Container for scrollable region ----
        scrollableFrame = ttk.Frame(self.controller)
        scrollableFrame.pack(fill="both", expand=True)

        # Use grid to make scrollbars align properly
        scrollableFrame.rowconfigure(0, weight=1)
        scrollableFrame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(scrollableFrame, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(scrollableFrame, orient="vertical", command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(scrollableFrame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Update scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.commit_ctx_menu, self.tree_ctx_menu, self.blob_ctx_menu = self._build_menus()

    def _get_vertex_rect(self, label):
        ids = self.canvas.find_withtag( label + ' && ' + self.VERTEX )
        return ids[0] if ids != () else None

    def _get_edge_line(self, srclabel, dstlabel):
        ids = self.canvas.find_withtag( srclabel + ' && ' + dstlabel + ' && ' + self.EDGE )
        return ids[0] if ids != () else None  

    def _get_vertex_dimensions(self, label):
        d = self.canvas.bbox(self._get_vertex_rect(label))
        if d == ():
            return d
        return ((d[2]-d[0])/2) - 1, ((d[3]-d[1])/2) - 1  

    def _get_vertex_text(self, label):
        ids = self.canvas.find_withtag( label + ' && ' + self.VERTEXLABEL )
        return ids[0] if ids != () else None 

    def _get_edge_text(self, srclabel, dstlabel):
        ids = self.canvas.find_withtag( srclabel + ' && ' + dstlabel + ' && ' + self.EDGELABEL )
        return ids[0] if ids != () else None 

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
        
    def _render_rect_shape(self, label:str, vtype:str, x1:int, y1:int, x2:int, y2:int):
        rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                          fill=self.vertex_render_params[vtype]['fill'],
                                          outline=self.vertex_render_params[vtype]['color'],
                                          width=self.vertex_render_params[vtype]['width'],
                                          tags = [label, vtype , self.VERTEX])
        text = self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=label, justify = tk.CENTER, 
                                       tags= [label, vtype, self.VERTEXLABEL])        

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

    def _build_menus(self):
        #context menus
        commit_ctx_menu = tk.Menu(self.controller, tearoff=0)
        commit_ctx_menu.add_command(label='Show related', command=self._context_load_commit_connected)
        tree_ctx_menu = tk.Menu(self.controller, tearoff=0)
        tree_ctx_menu.add_command(label='Show tree', command=self._context_show_commit_tree)
        tree_ctx_menu.add_command(label='Hide tree', command=self._context_hide_tree)
        blob_ctx_menu = tk.Menu(self.controller, tearoff=0)
        blob_ctx_menu.add_command(label='Show this path only', command=self._context_show_specific_path)
        return commit_ctx_menu, tree_ctx_menu, blob_ctx_menu

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
        self.controller.add_user_action( ('show_commit_related', vlabel) )
        ok = self.model.load_commit_related(vlabel, self.model.vertices[vlabel].get('x'),
                                            self.model.vertices[vlabel].get('y') + 40)
        if ok:
            self.render_model()
        self._context_click = None

    def _context_show_commit_tree(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        self.controller.add_user_action( ('show_tree', vlabel) )
        ok = self.model.load_tree_contents(vlabel, self.model.vertices[vlabel].get('x'), 
                                           self.model.vertices[vlabel].get('y') + 60)
        if ok:
            self.render_model()
        self._context_click = None

    def _context_show_specific_path(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        self.model.build_filter(vlabel)
        self.model.apply_filter()
        self.controller.update_status_bar()
        self.render_model()
        self._context_click = None

    def _context_hide_tree(self):
        if not self._context_click:
            return
        x, y = self._context_click
        vlabel = self.find_vertex_at(x, y)
        if vlabel is not None:
            #self._user_actions.append( ('hide_tree', vlabel) )
            print('action should be appended')
            self.model.hide_tree(vlabel)
            self.render_model()
        self._context_click = None

    def find_vertex_at(self, x, y):
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(items):
            tags = self.canvas.gettags(item)
            # look for VERTEX tag to identify vertex rectangle
            if self.VERTEX in tags:
                return tags[0]  # first tag is the vertex label
        return None

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
                messagebox.showerror("Vertex label", f"Cannot create vertex. Label '{lbl}' is empty or already exists.", parent=self.controller)
            except Exception:
                pass
            return None
        # draw a rectangle vertex (rx, ry are half-width/half-height) using dispatch dictionary
        self.vertex_render[used_type](labelid, used_type, x - rx, y - ry, x + rx, y + ry)
        return labelid

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

    def create_edge(self, srclabel, dstlabel, edge_type=True, label=None):
        if not self.model.add_edge(srclabel, dstlabel, edge_type=edge_type, label=label):
            return
        self._create_edge_line(srclabel, dstlabel, edge_type, label)

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

    def render_model(self):
        # check if vertex exists in GUI, if not, create it
        for labelid in self.model.vertices:
            rect = self._get_vertex_rect(labelid)           
            if rect is None:
                # skip tree/blob vertices if configured so
                if not self.show_trees and self.model.vertices[labelid].get('type') in ['tree', 'blob']:
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
                if not self.show_trees and (self.model.vertices[s_v].get('type') in ['tree', 'blob'] or
                                             self.model.vertices[d_v].get('type') in ['tree', 'blob']):
                    continue
                self._create_edge_line(s_v, d_v, edge_type, edge_label)
        # delete tree/blob vertices and edges if configured so, but do not modify model
        if not self.show_trees:
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
                                       outline=self.vertex_render_params[self.model.vertices[vlabel].get('type')]['color'])
            except Exception:
                pass
        self._drag_data['vertex'] = None
        # Update scroll region if drawing expands bounds
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_right_button_down(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        vlabel = self.find_vertex_at(x, y)
        
        menu_map = {
            'commit': self.commit_ctx_menu,
            'tagobject': self.commit_ctx_menu,
            'tree': self.tree_ctx_menu,
            "blob": self.blob_ctx_menu,
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

    def on_update_model(self):
        # clear existing GUI
        self.canvas.delete("all")
        # if init commit is available in model, it will be rendered
        self._init_commit = self.model.init_commit
        self.render_model()

    def on_new_model(self, pModel):
        self.model = pModel
        self.on_update_model()

    def build_bindings(self):
        # self.bind('<Delete>', self.on_delete_key) disabled delete
        self.canvas.bind('<Button-1>', self.on_left_button_down)
        self.canvas.bind('<B1-Motion>', self.on_left_button_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_left_button_up)
        self.canvas.bind('<Button-3>', self.on_right_button_down)

