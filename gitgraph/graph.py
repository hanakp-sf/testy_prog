import tkinter as tk
import sys, os, math, queue

from gui_settings import UserSettings
from model import GraphModel
import view

threadresult = False
class GraphApp(tk.Tk):
    def __init__(self, pModel=None):
        super().__init__()

        # link model
        self.model = pModel if pModel else GraphModel()
        self._load_model = None

        self.geometry("900x600")
        self.minsize(400, 500)

        # link view
        self.view = view.GraphView(self, self.model)

        # thread sync queue
        self._queue = queue.Queue()

        ## Load settings
        # whether to show tree/blob vertices and edges
        self._settings = UserSettings()
        self._settings.load()
        self._show_trees = tk.BooleanVar(value=self._settings.get_show_tree())
        self.view.show_trees = self._show_trees.get()

        self._current_file = None
        # list of user actions for debugging entry = ('action', 'object_label')
        self._user_actions = [] 

        # Default status message
        self.DEFAULT_MESSAGE = (
            "Left-click+drag vertex: move vertex.\n"
            "Right-click vertex: context menu."
        )
        
        self.status = tk.Label(self, text=self.DEFAULT_MESSAGE, anchor='w', justify='left')
        self.status.pack(side="bottom", fill=tk.X)

        # trigger function execution on exit
        self.protocol("WM_DELETE_WINDOW", self.on_exit) 

    def on_exit(self):
        self._settings.save()
        self.destroy()


if __name__ == '__main__':
    startup = 'NOPARAMS'
    # usage: python graph.py <path-to-git-repo>/<diagram-file>
    if len(sys.argv) == 2:
        # check arguments
        param = sys.argv[1]
        startup = 'GITDIR' if os.path.isdir(param) else 'DIAGRAMFILE'
    # model and view are created within App
    app = GraphApp()
    # render empty model
    #TBD app.on_new_model()
    
    # load only branch vertices and tip commits for fast startup
    '''
    TBD
    try:
        if startup == 'GITDIR':
            app.open_folder(param)
        if startup == 'DIAGRAMFILE':
            app.open_file(param)
    except Exception:
        pass
    '''
    app.mainloop()