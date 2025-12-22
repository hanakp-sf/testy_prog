import os, json

APP_NAME = "GitGraph"
MAX_MRU = 10

class UserSettings:
    def __init__(self, max_items=5):
        # If Python is installed from Microsoft Store
        # roaming app path is redirected to:
        # <user_profile>\AppData\Local\Packages\<Python_installation>\LocalCache\Roaming\
        path = os.environ["APPDATA"]
        self.file_path = os.path.join(path, APP_NAME)
        os.makedirs(self.file_path, exist_ok=True)
        self.file_path = os.path.join(self.file_path, "settings.json")
        self.max_items = max_items
        self._show_tree = True
        #self.mru = self.load()
        self.mru = []

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.mru = data.get("mru", [])
                self._show_tree = data.get("show_tree", True)
        except:
            self.mru = []
            self._show_tree = True

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump({"mru": self.mru, "show_tree": self._show_tree}, f, indent=4)

    def add_file(self, filepath):
        filepath = os.path.abspath(filepath)

        # Remove if already in list
        if filepath in self.mru:
            self.mru.remove(filepath)

        # Insert at top
        self.mru.insert(0, filepath)

        # Limit size
        if len(self.mru) > self.max_items:
            self.mru = self.mru[:self.max_items]

    def remove_file(self, filepath):
        # Remove if in list
        if filepath in self.mru:
            self.mru.remove(filepath)

    def get_mru_list(self):
        return self.mru

    def get_show_tree(self):
        return self._show_tree

    def set_show_tree(self, value):
        self._show_tree = value
    
