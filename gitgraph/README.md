# Interactive Directed Graph Creator (Tkinter)

This small Python GUI allows interactive creation of a directed graph with rectangle vertices and oriented edges.

Features
- Left-click empty area: create a vertex.
- Left-click + drag a vertex: move it (connected edges update).
- Right-click + drag from one vertex to another: create a directed edge (arrow).
- Double-click a vertex label: rename it.
- Select a vertex (it shows a red outline) and press `Delete`: removes the vertex and its connected edges.

Requirements
- Python 3.x (Tkinter is part of the standard library on most OSes).

Run
In a Windows `cmd.exe` terminal, run:

```cmd
cd c:\personal\github_testy_prog\gitgraph
python graph_gui.py
```

Notes
- No external packages are required.
- The app does not persist graphs to disk (you can extend it to save/load if needed).

If you'd like, I can add save/load (JSON), edge deletion, or export to an image.
