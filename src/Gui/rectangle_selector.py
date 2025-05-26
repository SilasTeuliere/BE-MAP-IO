# manual_selector.py

from matplotlib.patches import Rectangle
import numpy as np
import matplotlib.dates as mdates

class ManualRectangleSelector:
    """
    Une classe pour gérer la sélection manuelle de rectangles sur un graphique matplotlib.
    """
    def __init__(self, ax, canvas_widget, data, on_select_callback):
        """
        Initialise le sélecteur de rectangle manuel.
        :param ax: L'axe matplotlib sur lequel dessiner le rectangle.
        :param canvas_widget: Le widget de la figure matplotlib.
        :param data: Les données à utiliser pour la sélection.
        :param on_select_callback: Fonction de rappel appelée avec les indices sélectionnés.
        """

        self.ax = ax
        self.canvas_widget = canvas_widget
        self.data = data
        self.on_select_callback = on_select_callback

        self.start_point = None
        self.current_rect_patch = None

        self.canvas_widget.mpl_connect("button_press_event", self.on_press)
        self.canvas_widget.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas_widget.mpl_connect("button_release_event", self.on_release)

    def on_press(self, event):
        """
        Gère l'événement de pression du bouton de la souris.
        :param event: L'événement de pression du bouton.
        """

        if event.inaxes != self.ax:
            return
        self.start_point = (event.xdata, event.ydata)
        if self.current_rect_patch:
            self.current_rect_patch.remove()
            self.current_rect_patch = None

    def on_motion(self, event):
        """
        Gère l'événement de mouvement de la souris.
        :param event: L'événement de mouvement de la souris.
        """

        if not self.start_point or event.inaxes != self.ax:
            return

        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        xmin, xmax = sorted([x0, x1])
        ymin, ymax = sorted([y0, y1])

        if self.current_rect_patch:
            self.current_rect_patch.set_bounds(xmin, ymin, xmax - xmin, ymax - ymin)
        else:
            self.current_rect_patch = Rectangle(
                (xmin, ymin), xmax - xmin, ymax - ymin,
                linewidth=1, edgecolor='red', facecolor='red', alpha=0.2
            )
            self.ax.add_patch(self.current_rect_patch)

        self.canvas_widget.draw_idle()

    def on_release(self, event):
        """
        Gère l'événement de relâchement du bouton de la souris.
        :param event: L'événement de relâchement du bouton.
        """
        
        if not self.start_point or event.inaxes != self.ax:
            return

        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        xmin, xmax = sorted([x0, x1])
        ymin, ymax = sorted([y0, y1])

        self.start_point = None

        x_data = mdates.date2num(self.data['datetime'])
        y_data = self.data['ccn_conc'].to_numpy()

        mask = (x_data >= xmin) & (x_data <= xmax) & (y_data >= ymin) & (y_data <= ymax)
        indices = np.where(mask)[0].tolist()

        if self.current_rect_patch:
            self.current_rect_patch.remove()
            self.current_rect_patch = None
            self.canvas_widget.draw_idle()

        if indices:
            self.on_select_callback(indices)
        else:
            print("Aucun point sélectionné.")