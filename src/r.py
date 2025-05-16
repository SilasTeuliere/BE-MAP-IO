import matplotlib
matplotlib.use("TkAgg")  # ← force le bon backend avec majuscules

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import numpy as np

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Test RectangleSelector")

        fig = Figure(figsize=(6, 4))
        self.ax = fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.x = np.random.rand(100)
        self.y = np.random.rand(100)
        self.ax.scatter(self.x, self.y)

        self.rs = RectangleSelector(
            self.ax,
            self.on_select,
            useblit=True,
            button=[1],
            minspanx=5,
            minspany=5,
            spancoords='data',
            interactive=False,
            props=dict(facecolor='red', edgecolor='black', alpha=0.3, fill=True)
        )

        self.canvas.get_tk_widget().focus_set()

    def on_select(self, eclick, erelease):
        print("Sélection détectée")
        xmin, xmax = sorted([eclick.xdata, erelease.xdata])
        ymin, ymax = sorted([eclick.ydata, erelease.ydata])
        mask = (self.x >= xmin) & (self.x <= xmax) & (self.y >= ymin) & (self.y <= ymax)
        indices = np.where(mask)[0]
        print(f"{len(indices)} point(s) sélectionné(s) :", indices)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()