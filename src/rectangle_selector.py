import matplotlib.pyplot as plt

class RectangleSelector:
    def __init__(self, ax, canvas_widget):
        self.ax = ax
        self.canvas_widget = canvas_widget
        self.x1, self.y1 = None, None
        self.rect = None

        self.canvas_widget.mpl_connect('button_press_event', self.on_click)
        self.canvas_widget.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas_widget.mpl_connect('button_release_event', self.on_release)

    def on_click(self, event):
        if event.mouseevent.button == 1 and event.inaxes == self.ax:
            self.x1, self.y1 = event.mouseevent.xdata, event.mouseevent.ydata
            print(f"Sélection initiale: x1={self.x1}, y1={self.y1}")

            if hasattr(self, 'rect'):
                self.rect.remove()
            self.rect = plt.Rectangle((self.x1, self.y1), 0, 0, fill=False, color='red')
            self.ax.add_patch(self.rect)
            self.canvas_widget.draw_idle()

    def on_motion(self, event):
        if self.x1 is None or event.inaxes != self.ax:
            return
        x2, y2 = event.xdata, event.ydata
        self.rect.set_width(x2 - self.x1)
        self.rect.set_height(y2 - self.y1)
        self.canvas_widget.draw_idle()

    def on_release(self, event):
        if self.x1 is None or event.inaxes != self.ax:
            return
        x2, y2 = event.xdata, event.ydata
        print(f"Sélection finale: x2={x2}, y2={y2}")
        # Filtrer les données ici en utilisant self.x1, x2, self.y1, y2
        self.x1, self.y1 = None, None