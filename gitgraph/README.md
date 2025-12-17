# Git Graph Creator (Tkinter)

This small Python GUI shows git graph of branches/commits/trees/blobs.

Features
- Left-click + drag a vertex: move it (connected edges update).
- Right-click: show contex menu for graph expansion.
- set filter to specific blob and all other blobs are hidden

Requirements
- Python 3.x (Tkinter is part of the standard library on most OSes).

Run
In a Windows `cmd.exe` terminal, run:

```cmd
python graph_gui.py
```

Notes
- No external packages are required.
- The app persist graphs to disk and update from git repo.


