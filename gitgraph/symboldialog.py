import tkinter as tk
from tkinter import Menu
import view
from model import GraphModel 

class SymbolDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Symbols")
        self.geometry("450x450")
        self.resizable(False, False)

        self.model = GraphModel()
        self.model.create_symbols_sample()
        self.view = view.GraphView(self, self.model)
        self.view.render_model()
        # Close button
        close_button = tk.Button(self, text="Close", command=self.destroy)
        close_button.pack(pady=(0, 10))