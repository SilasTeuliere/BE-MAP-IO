import tkinter as tk
import numpy as np
import matplotlib.dates as mdates
import pandas as pd
import os
import math
from tkinter import messagebox
from tkinter import Toplevel, scrolledtext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import date2num
from . import rectangle_selector


def delete_selected_points(self):
    """
    Supprime les points actuellement sélectionnés dans la page affichée.

    Les points sont enregistrés dans un fichier `_deleted.csv` pour être restaurables,
    et la suppression est ajoutée à l'historique pour permettre un undo.
    """

    #print("delete_selected_points, selected_indices =", self.selected_indices)
    if not self.selected_indices:
        messagebox.showwarning("Suppression", "Aucun point sélectionné à supprimer.")
        return
    global_indices = [self.current_slice_indices[i] for i in self.selected_indices if 0 <= i < len(self.current_slice_indices)]
    if not global_indices:
        messagebox.showwarning("Suppression", "Les indices sélectionnés sont invalides.")
        return
    previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
    self.history.append((self.data.copy(), previous_deleted))
    deleted = self.data.loc[global_indices]
    deleted_file_path = os.path.splitext(self.file_path)[0] + "_deleted.csv"
    try:
        old_deleted = pd.read_csv(deleted_file_path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        old_deleted = pd.DataFrame()

    self.deleted_data = pd.concat([old_deleted, deleted], ignore_index=True)
    self.deleted_data.to_csv(deleted_file_path, index=False)
    self.data = self.data.drop(index=global_indices).reset_index(drop=True)
    self.selected_indices = []
    self.display_scatter_plot()


def clear_data(self):
    """
    Supprime toutes les données chargées dans le graphique actuel.

    Sauvegarde l'état actuel dans l'historique pour permettre une restauration.
    Réinitialise les sélections et les données supprimées.
    """
    
    if self.data is not None and not self.data.empty:
        previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
        self.history.append((self.data.copy(), previous_deleted))

        self.data = self.data.iloc[0:0]
        self.selected_indices = []

        self.deleted_data = pd.DataFrame()

        self.display_scatter_plot()
    else:
        messagebox.showwarning("Suppression", "Aucune donnée à supprimer")
        

def undo_last(self):
    """
    Annule la dernière action effectuée (suppression ou modification).

    Restaure les données et les données supprimées à leur état précédent.
    """

    if self.history:
        self.data, self.deleted_data = self.history.pop()
        self.display_scatter_plot()
        deleted_file_path = os.path.splitext(self.file_path)[0] + "_deleted.csv"
        self.deleted_data.to_csv(deleted_file_path, index=False)
    else:
        messagebox.showwarning("Annulation", "Aucune action à annuler.")


def undo_all(self):
    """
    Annule toutes les actions effectuées depuis le début de la session.

    Restaure les données à leur état initial.
    """

    if self.history:
        self.data, self.deleted_data = self.history[0]
        self.history = []
        self.display_scatter_plot()
    else:
        messagebox.showwarning("Annulation", "Aucune action à annuler.")


def open_multiplier_window(self):
    """
    Affiche une fenêtre pour appliquer un coefficient multiplicateur aux colonnes numériques.

    Enregistre l'état actuel pour permettre une restauration.
    """

    multiplier_window = tk.Toplevel()
    multiplier_window.title("Coefficient Multiplicateur")
    multiplier_window.geometry("400x200")
    label = tk.Label(multiplier_window, text="Indiquer le coefficient multiplicateur :", font=("Arial", 12))
    label.pack(pady=10)
    coeff_entry = tk.Entry(multiplier_window, font=("Arial", 12), width=10)
    coeff_entry.pack(pady=5)

    def validate_multiplier():
        coeff = coeff_entry.get()
        try:
            coeff = float(coeff)
            if self.data is not None:
                previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
                self.history.append((self.data.copy(), previous_deleted))

                for col in self.data.columns:
                    if col != "datetime" and pd.api.types.is_numeric_dtype(self.data[col]):
                        self.data[col] = self.data[col] * coeff

                self.display_scatter_plot()
            multiplier_window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")
            coeff_entry.delete(0, tk.END)

    validate_button = tk.Button(multiplier_window, text="Valider", command=validate_multiplier)
    validate_button.pack(pady=10)


# def open_multiplier_window(self):
#     """
#     Affiche une fenêtre pour appliquer un coefficient multiplicateur a la colonne Ccn_conc.

#     Enregistre l'état actuel pour permettre une restauration.
#     """

#     multiplier_window = tk.Toplevel()
#     multiplier_window.title("Coefficient Multiplicateur")
#     multiplier_window.geometry("400x200")
#     label = tk.Label(multiplier_window, text="Indiquer le coefficient multiplicateur :", font=("Arial", 12))
#     label.pack(pady=10)
#     coeff_entry = tk.Entry(multiplier_window, font=("Arial", 12), width=10)
#     coeff_entry.pack(pady=5)
#     def validate_multiplier():
#         coeff = coeff_entry.get()
#         try:
#             coeff = float(coeff)
#             if self.data is not None:
#                 previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
#                 self.history.append((self.data.copy(), previous_deleted))

#                 # Only modify the 'ccn_conc' column if it exists and is numeric
#                 if "ccn_conc" in self.data.columns and pd.api.types.is_numeric_dtype(self.data["ccn_conc"]):
#                     self.data["ccn_conc"] = self.data["ccn_conc"] * coeff

#                 self.display_scatter_plot()
#             multiplier_window.destroy()
#         except ValueError:
#             messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")
#             coeff_entry.delete(0, tk.END)

#     validate_button = tk.Button(multiplier_window, text="Valider", command=validate_multiplier)
#     validate_button.pack(pady=10)


def invalidate_series(self):
    """
    Supprime tous les points de la page courante sans sélection manuelle.

    Utilise `delete_selected_points` en simulant une sélection complète.
    """

    if self.current_slice is None or self.current_slice.empty:
        messagebox.showinfo("Suppression", "Aucune donnée à supprimer dans cette page.")
        return

    self.selected_indices = list(range(len(self.current_slice)))

    self.delete_selected_points()


def show_statistics(self):
    """
    Affiche des statistiques descriptives des données actuellement chargées.

    Utilise `pandas.describe()` pour produire un résumé statistique.
    """

    if self.data is not None:
        stats = self.data.describe().to_string()

        stats_window = Toplevel()
        stats_window.title("Statistiques")
        stats_window.geometry("800x400")

        text_area = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD, font=("Courier", 10))
        text_area.pack(expand=True, fill='both')
        text_area.insert(tk.END, stats)
        text_area.config(state='disabled')

    else:
        tk.messagebox.showwarning("Statistiques", "Aucune donnée disponible")


def show_shortcuts(self):
    """
    Affiche une fenêtre contenant les raccourcis clavier disponibles pour l'utilisateur.
    """

    shortcut_window = tk.Toplevel()
    shortcut_window.title("Raccourcis clavier")
    shortcut_window.geometry("900x400")

    shortcuts = (
        "Importer un Fichier CSV : Ctrl + O / Cmd + O sur Mac\n"
        "Sauvegarder le fichier :  Ctrl + S / Cmd + S sur Mac\n"
        "Supprimer données sélectionnées  :  Ctrl + X / Cmd + X sur Mac\n"
        "Supprimer l’ensemble des données  :  Ctrl + U / Cmd + U sur Mac\n"
        "Appliquer un coefficient multiplicateur :  Ctrl + P / Cmd + P sur Mac\n"
        "Annuler la dernière modification :  Ctrl + Z / Cmd + Z sur Mac\n"
        "Annuler toutes les  modifications :  Ctrl + Shift + Z / Cmd + Shift + Z sur Mac\n"
        "Invalider toute la série de données :  Ctrl + I / Cmd + I sur Mac\n"
        "Affichage Statistique :  Ctrl + A / Cmd + A sur Mac\n"
        "Zoom + : Ctrl + '+' ou Ctrl + '=' / Cmd + '+' ou Cmd + '='\n"
        "Zoom - : Ctrl + '-' / Cmd + '-'\n"
    )

    text_widget = tk.Text(shortcut_window, wrap=tk.WORD, font=("Arial", 12), padx=10, pady=10)
    text_widget.pack(expand=True, fill=tk.BOTH)

    text_widget.tag_configure("bold", font=("Arial", 12, "bold"))

    for line in shortcuts.split("\n"):
        if line:
            before_colon, after_colon = line.split(":", 1)
            text_widget.insert(tk.END, before_colon, "bold")
            text_widget.insert(tk.END, " :")
            text_widget.insert(tk.END, after_colon + "\n")

    close_button = tk.Button(shortcut_window, text="Ok", command=shortcut_window.destroy)
    close_button.pack(pady=10)

    text_widget.config(state=tk.DISABLED)


def show_about(self):
    """
    Affiche une fenêtre "À propos" avec le nom de l'application et les auteurs.
    """

    messagebox.showinfo(
        "À propos",
        "ClearCCNData v1.0\n\nApplication de visualisation de données environnementales.\nDéveloppée par :\nFanny Barcelo \nGhodbane Nour Elhouda \nMa-ida Salifou-Bawa \nSilas Teuliere."
    )   


def zoom_plot(self, factor, event = None):
    """
    Effectue un zoom sur le graphique, centré sur la souris si un événement est fourni.

    Parameters:
        factor (float): Le facteur de zoom (ex: 0.8 pour zoom avant, 1.2 pour zoom arrière).
        event (MouseEvent, optional): L'événement de souris pour centrer le zoom.
    """
    
    if not hasattr(self, 'ax') or self.ax is None:
        return

    xlim = self.ax.get_xlim()
    ylim = self.ax.get_ylim()

    if event is None or event.xdata is None or event.ydata is None:
        xcenter = (xlim[0] + xlim[1]) / 2
        ycenter = (ylim[0] + ylim[1]) / 2
    else:
        xcenter = event.xdata
        ycenter = event.ydata

    xwidth = (xlim[1] - xlim[0]) * factor / 2
    yheight = (ylim[1] - ylim[0]) * factor / 2

    self.ax.set_xlim([xcenter - xwidth, xcenter + xwidth])
    self.ax.set_ylim([ycenter - yheight, ycenter + yheight])
    self.canvas_widget.draw_idle()

def on_scroll_zoom(self, event):
    ctrl_pressed = event.key == 'control' or event.key == 'cmd'

    if ctrl_pressed:
        if event.button == 'up':
            self.zoom_plot(0.8, event)
        elif event.button == 'down':
            self.zoom_plot(1.2, event)

def highlight_points(self, indices):
    if self.highlight:
        self.highlight.remove()
    self.selected_indices = indices
    xdata = self.current_slice['datetime'].iloc[indices]
    ydata = self.current_slice['ccn_conc'].iloc[indices]
    self.highlight = self.ax.scatter(xdata, ydata, color='red', s=80, edgecolors='black', zorder=10)
    self.canvas_widget.draw_idle()

def on_select(self, eclick, erelease):
    if self.data is None:
        return
    if eclick.xdata is None or erelease.xdata is None:
        messagebox.showinfo("Sélection", "Clic hors des axes.")
        return
    xmin, xmax = sorted([eclick.xdata, erelease.xdata])
    ymin, ymax = sorted([eclick.ydata, erelease.ydata])
    print("Rectangle :", xmin, xmax, ymin, ymax)
    x_data = mdates.date2num(self.data['datetime'])
    y_data = self.data['ccn_conc'].to_numpy()
    mask = (x_data >= xmin) & (x_data <= xmax) & (y_data >= ymin) & (y_data <= ymax)
    indices = np.where(mask)[0].tolist()

    if not indices:
        messagebox.showinfo("Sélection", "Aucun point sélectionné.")
        return

    self.selected_indices = indices
    self.highlight_points(indices)
    print(f"{len(indices)} point(s) sélectionné(s) par rectangle.")

def on_click(self, event):
    if event.mouseevent.button == 1 and event.artist == self.scatter_points:
        x = self.current_slice['datetime'].to_numpy()
        y = self.current_slice['ccn_conc'].to_numpy()

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        norm_x_click = (event.mouseevent.xdata - xlim[0]) / (xlim[1] - xlim[0])
        norm_y_click = (event.mouseevent.ydata - ylim[0]) / (ylim[1] - ylim[0])
        norm_x = (mdates.date2num(x) - xlim[0]) / (xlim[1] - xlim[0])
        norm_y = (y - ylim[0]) / (ylim[1] - ylim[0])

        distances = np.hypot(norm_x - norm_x_click, norm_y - norm_y_click)
        idx = np.argmin(distances) 

        print(f"Point sélectionné : ({x[idx]}, {y[idx]})")

        self.highlight_points([idx])
        self.selected_indices = [idx]
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.canvas_widget.draw_idle()


def clear_selection(self):
    if self.highlight:
        self.highlight.remove()
        self.highlight = None
        self.canvas_widget.draw_idle()
    self.selected_indices = []

def on_rectangle_select(self, indices):
    self.selected_indices = indices
    self.highlight_points(indices)

def next_slice(self):
    if self.current_page < len(self.pages) - 1:
        self.current_page += 1
        self.display_scatter_plot()
        self.next_button.config(state="disabled" if self.current_page == len(self.pages)-1 else "normal")
        self.prev_button.config(state="normal")

def previous_slice(self):
    if self.current_page > 0:
        self.current_page -= 1
        self.display_scatter_plot()
        self.prev_button.config(state="disabled" if self.current_page == 0 else "normal")

def create_logical_pages(self, min_points=5000, max_gap_minutes=2):
    if self.data is None:
        self.pages = []
        return

    self.data = self.data.sort_values("datetime").reset_index(drop=True)

    pages = []
    start_idx = 0
    last_time = self.data["datetime"].iloc[0]

    for i in range(1, len(self.data)):
        current_time = self.data["datetime"].iloc[i]
        gap = (current_time - last_time).total_seconds() / 60
        if ((i - start_idx >= min_points) and (gap >= max_gap_minutes)) or (gap > 30):
            pages.append((start_idx, i))
            start_idx = i

        last_time = current_time

    pages.append((start_idx, len(self.data)))
    self.pages = pages
    self.current_page = 0


def add_color_legend(self):
    if hasattr(self, 'legend_frame'):
        self.legend_frame.destroy()

    self.legend_frame = tk.Frame(self.inner_frame)
    self.legend_frame.pack(side=tk.TOP, anchor="w", padx=10, pady=5)

    tk.Label(self.legend_frame, text="Légende des couleurs :", font=("Arial", 10, "bold")).pack(anchor="w")

    legend_colors = {
        0.1: "purple",
        0.2: "blue",
        0.3: "cyan",
        0.4: "green",
        0.5: "yellow",
        0.6: "orange",
        0.7: "pink",
        0.8: "red",
        0.9: "brown",
        1.0: "black"
    }

    for val, color in legend_colors.items():
        item = tk.Frame(self.legend_frame)
        item.pack(anchor="w", pady=1)
        canvas = tk.Canvas(item, width=15, height=15)
        canvas.create_oval(2, 2, 13, 13, fill=color, outline="black")
        canvas.pack(side=tk.LEFT)
        tk.Label(item, text=f"Sursaturation {val}", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
    
def display_scatter_plot(self):
    if hasattr(self, 'scatter_points'):
        self.scatter_points.remove()
    if self.data is None or not hasattr(self, 'pages') or not self.pages:
        return
    if "datetime" not in self.data.columns or "ccn_conc" not in self.data.columns:
        messagebox.showwarning("Visualisation", "Colonnes 'datetime' et 'ccn_conc' requises")
        return

    if(len(self.pages) > 1):
        self.next_button.config(state="normal")

    self.data["datetime"] = pd.to_datetime(self.data["datetime"], errors='coerce')
    self.data = self.data.dropna(subset=["datetime", "ccn_conc"])

    start, end = self.pages[self.current_page]
    data_slice = self.data.iloc[start:end]

    self.current_slice = data_slice.copy()
    self.current_slice_indices = list(data_slice.index)

    for widget in self.inner_frame.winfo_children():
        widget.destroy()

    num_points = len(data_slice)
    height = max(20, num_points / 500)
    fig = Figure(figsize=(height, 15))
    self.ax = fig.add_subplot(111)
    fig.tight_layout()

    colors = data_slice["ccn_sursaturation"].map({
    0.1: "purple",
    0.2: "blue",
    0.3: "cyan",
    0.4: "green",
    0.5: "yellow",
    0.6: "orange",
    0.7: "pink",
    0.8: "red",
    0.9: "brown",
    1.0: "black"
    }).fillna("gray")
    
    self.scatter_points = self.ax.scatter(
        data_slice["datetime"],
        data_slice["ccn_conc"],
        c=colors,
        alpha=0.5,
        picker=True
    )

    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))
    self.ax.xaxis.set_major_locator(MaxNLocator(min(1000, max(10, num_points // 500))))

    date_min = data_slice["datetime"].min().strftime('%d/%m/%Y %H:%M:%S')
    date_max = data_slice["datetime"].max().strftime('%d/%m/%Y %H:%M:%S')
    self.ax.set_title(f"Page {self.current_page + 1}/{len(self.pages)} — du {date_min} au {date_max}")
    self.ax.grid(True)
    fig.autofmt_xdate(rotation=45)
    fig.subplots_adjust(bottom=0.25)

    self.canvas_widget = FigureCanvasTkAgg(fig, master=self.inner_frame)
    self.canvas_widget.draw()
    self.canvas_widget.get_tk_widget().pack(fill=tk.X, expand=True)
    self.canvas_widget.mpl_connect('pick_event', self.on_click)
    self.canvas_widget.mpl_connect("scroll_event", self.on_scroll_zoom)

    if hasattr(self, 'rs') and self.rs is not None:
        self.rs.set_active(False)
        del self.rs

    self.selector = rectangle_selector.ManualRectangleSelector(
        self.ax,
        self.canvas_widget,
        data_slice,
        self.on_rectangle_select
    )

    self.add_color_legend()
