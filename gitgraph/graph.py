import tkinter as tk
from tkinter import filedialog, messagebox
import sys, os, queue, threading

from gui_settings import UserSettings
from model import GraphModel
import symboldialog
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
        self.view.build_bindings()

        # thread sync queue
        self._queue = queue.Queue()

        ## Load settings
        # whether to show tree/blob/tag/remote branch vertices and edges
        self._settings = UserSettings()
        self._settings.load()
        self.view.show_trees.set(self._settings.get_show_tree())
        self.view.show_tags.set(self._settings.get_show_tag())
        self.view.show_rbranches.set(self._settings.get_show_rbranch())
        # whether to load tag/remote branch
        self._load_tags = tk.BooleanVar(value=self._settings.get_load_tags())
        self._load_rbranches = tk.BooleanVar(value=self._settings.get_load_rbranches())

        self._current_file = None
        # list of user actions for debugging entry = ('action', 'object_label')
        self._user_actions = [] 

        # Default status message
        self.DEFAULT_MESSAGE = "Left-click+drag vertex: move vertex. Right-click vertex: context menu."

        # build menubar and context menu
        self.menubar, self.file_menu = self._build_menus()
        self.config(menu=self.menubar)
        
        self.status = tk.Label(self, text=self.DEFAULT_MESSAGE, anchor='w', justify='left')
        self.status.pack(side="bottom", fill=tk.X)

        # trigger function execution on exit
        self.protocol("WM_DELETE_WINDOW", self.on_exit) 

    def _build_menus(self):
        # Main menu bar 
        menubar = tk.Menu(self)
        # File menu
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
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='Reset filter', command=self._menu_view_reset)
        view_menu.add_command(label='Refresh from Repo', command=self._menu_view_refresh)
        view_menu.add_separator()    
        view_menu.add_checkbutton(label='Show containers', 
                                  onvalue=True, offvalue=False,
                                  variable=self.view.show_trees,
                                  command=self._toggle_show_trees)
        view_menu.add_checkbutton(label='Show tags', 
                                  onvalue=True, offvalue=False,
                                  variable=self.view.show_tags,
                                  command=self._toggle_show_tags)
        view_menu.add_checkbutton(label='Show remote branches', 
                                  onvalue=True, offvalue=False,
                                  variable=self.view.show_rbranches,
                                  command=self._toggle_show_rbranches)
        view_menu.add_separator() 
        view_menu.add_command(label='Print model', command=self._menu_print_model)
        view_menu.add_command(label='Print actions', command=self._menu_print_actions)
        menubar.add_cascade(label='View', menu=view_menu)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_checkbutton(label='Include tags',
                                  onvalue=True, offvalue=False,
                                  variable=self._load_tags,
                                  command=self._toggle_load_tags
                                  )
        settings_menu.add_checkbutton(label='Include remote branches', 
                                  onvalue=True, offvalue=False,
                                  variable=self._load_rbranches,
                                  command=self._toggle_load_rbranches
                                  )
        menubar.add_cascade(label='Settings', menu=settings_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='Symbols', command=self._menu_help_symbols)
        menubar.add_cascade(label='Help', menu=help_menu)
        return menubar, file_menu

    def _menu_open_folder(self):
        """Open a git repository folder and load its branches."""
        try:
            folder = filedialog.askdirectory(title="Select Git repository folder", mustexist=True)
        except Exception:
            folder = None
        if folder:
            self.open_folder(folder)
    
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

    def _menu_exit_app(self):
        self._settings.save()
        self.quit()

    def _menu_view_reset(self):
        self.model.reset_filter()
        self.model.apply_filter()
        self.view.render_model()
        self.update_status_bar()

    def _menu_view_refresh(self):
        global threadresult

        self.menubar.entryconfig('View', state='disabled')
        self.update_status_bar(f'Refreshing ...', 'red')
        threadresult = False
        self.after(100, self.process_queue)
        # trigger model refresh from git folder
        loader = threading.Thread(target=self.refresh_from_folder, daemon=True)
        loader.start()

    def _menu_print_model(self):
        """Print the current model to the console for debugging."""
        try:
            print("Vertices:")
            for vlabel, v in self.model.vertices.items():
                print(f"  {vlabel}: type='{v.get('type')}', pos=({v.get('x')},{v.get('y')}), visible={v.get('visible')}")
            print("Edges:")
            for e in self.model.edges:
                print(f"  {e}")
        except Exception as e:
            print(f"Error printing model: {e}")

    def _menu_print_actions(self):
        """Print the list of user actions to the console for debugging."""
        try:
            print("User actions:")
            for action in self._user_actions:
                print(f"  {action}")
        except Exception as e:
            print(f"Error printing actions: {e}")

    def _menu_help_symbols(self):
        symboldialog.SymbolDialog(self)

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

    def update_status_bar(self, message = None, color = 'black'):
        if message is None: 
            status = f'Tags: {'ON' if self.model._include_tags else 'OFF'} | Remote branches: {'ON' if self.model._include_rbranches else 'OFF'}'
            if len(self.model._filter) > 0:
                self.status.config(text = f'{status} | Filter path: {self.model.get_filter_as_string()}',  fg = 'red')
            else:
                self.status.config(text = f'{status} | {self.DEFAULT_MESSAGE}', fg = color)
        else:
            self.status.config(text = message, fg = color)

    def update_title(self):
        new_title = '<untitled>'

        if self.model.repo_dir:
            new_title = self.model.repo_dir + ' (' + ('<untitled>' if self._current_file is None else self._current_file) + ')'
        self.title("Git graph for " + new_title)

    def add_user_action(self, action):
        self._user_actions.append(action)

    def _toggle_show_trees(self):
        #variable is toggled, just render
        newvalue = self.view.show_trees.get()
        self._settings.set_show_tree(newvalue)
        self._user_actions.append( ('toggle_show_trees', '->' + str(newvalue)) )
        self.view.render_model()

    def _toggle_show_tags(self):
        #variable is toggled, just render
        newvalue = self.view.show_tags.get()
        self._settings.set_show_tag(newvalue)
        self._user_actions.append( ('toggle_show_tags', '->' + str(newvalue)) )
        self.view.render_model()       

    def _toggle_show_rbranches(self):
        #variable is toggled, just render
        newvalue = self.view.show_rbranches.get()
        self._settings.set_show_rbranch(newvalue)
        self._user_actions.append( ('toggle_show_rbranches', '->' + str(newvalue)) )
        self.view.render_model() 

    def _toggle_load_tags(self):
        #variable is toggled, will be used during next load/reload
        self._settings.set_load_tags(self._load_tags.get())
        self._user_actions.append( ('toggle_load_tags', '->' + str(self._load_tags.get())) )

    def _toggle_load_rbranches(self):
        #variable is toggled, will be used during next load/reload
        self._settings.set_load_rbranches(self._load_rbranches.get()) 
        self._user_actions.append( ('toggle_load_rbranches', '->' + str(self._load_rbranches.get())) )

    def on_exit(self):
        self._settings.save()
        self.destroy()

    def on_new_model(self):
        self.view.on_new_model(self.model)
        self.update_status_bar()
        self.update_title()

    def on_update_model(self):
        self.view.on_update_model()
        self.update_status_bar()
        self.update_title()      

    def refresh_from_folder(self):
        '''
        Background job to refresh model from git folder
        '''    
        global threadresult

        res = self.model.reload_refs(include_tags=self._load_tags.get(), include_rbranches=self._load_rbranches.get())
        threadresult = res
        self._queue.put("REFRESHEDFOLDER")

    def load_from_folder(self, gitfolder:str):
        '''
        Background job to load model from git folder
        '''
        global threadresult

        self._load_model = GraphModel()
        self._load_model.load_refs(gitfolder, include_tags=self._load_tags.get(), include_rbranches=self._load_rbranches.get())
        self._queue.put("LOADEDFOLDER")

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
                    self.on_update_model()
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

    def open_file(self, filepath):
        try:
            self.model.load_from_file(filepath)
            self._current_file = filepath
            self.on_update_model()
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
    app.on_update_model()
    
    # load only branch vertices and tip commits for fast startup
    try:
        if startup == 'GITDIR':
            app.open_folder(param)
        if startup == 'DIAGRAMFILE':
            app.open_file(param)
    except Exception:
        pass

    app.mainloop()