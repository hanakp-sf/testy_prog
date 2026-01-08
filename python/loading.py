import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
'''
Example of using long running task within Tkinner. Task is processed in separate thread and end of processing
is reported back to main thread via queue
'''
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Background Task Example")
        self.geometry("400x200")

        # Queue for thread communication
        self.queue = queue.Queue()

        # UI Elements
        self.start_button = ttk.Button(
            self, text="Start Long Task", command=self.start_task
        )
        self.start_button.pack(pady=40)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.info = 'init:'



    def start_task(self):
        """Start the background task."""
        self.status_var.set("Task started...")
        self.start_button.config(state=tk.DISABLED)
        print(f'before: {self.info}')
        # Poll queue periodically
        self.after(100, self.process_queue)
        worker = threading.Thread(target=self.long_running_task, args=('Passed value',), daemon=True)
        worker.start()

    def long_running_task(self, val:str=None):
        """Simulate a long-running operation."""
        time.sleep(5)  # Simulate work
        self.info = val
        self.queue.put("Task completed")

    def process_queue(self):
        """Process messages from the background thread."""
        try:
            message = self.queue.get_nowait()
        except queue.Empty:
            # Continue polling
            self.after(100, self.process_queue)
        else:
            self.status_var.set(message)
            self.start_button.config(state=tk.NORMAL)
            print(f'after: {self.info}')


if __name__ == "__main__":
    app = App()
    app.mainloop()
