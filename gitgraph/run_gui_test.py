import sys
import traceback

try:
    # Import the GUI module and instantiate it without entering mainloop.
    from graph_gui import GraphGUI
    from graph_model import GraphModel
    model = GraphModel()
    model.load_sample()
    app = GraphGUI(model=model)
    # Try a single update to initialize Tk, then destroy to avoid blocking.
    app.update()
    app.destroy()
    print("GUI started and destroyed successfully")
except Exception:
    print("ERROR during GUI startup")
    traceback.print_exc()
    sys.exit(1)
