import tkinter as tk
from tkinter import ttk
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

