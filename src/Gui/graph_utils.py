import tkinter as tk
import numpy as np
import matplotlib.dates as mdates
import pandas as pd
import os
from datetime import timedelta
from tkinter import messagebox
from tkinter import Toplevel, scrolledtext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import date2num
from . import rectangle_selector


def delete_selected_points(self):
    print("delete_selected_points, selected_indices =", self.selected_indices)
    if not self.selected_indices:
        messagebox.showwarning("Suppression", "Aucun point sélectionné à supprimer.")
        return

    # Sauvegarde pour undo
    previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
    self.history.append((self.data.copy(), previous_deleted))

    # Extrait les lignes à supprimer
    deleted = self.data.iloc[self.selected_indices]

    # Construit le path du fichier deleted.csv
    deleted_file_path = os.path.splitext(self.file_path)[0] + "_deleted.csv"

    # Lecture robuste de l'ancien deleted.csv
    try:
        old_deleted = pd.read_csv(deleted_file_path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        old_deleted = pd.DataFrame()

    # Concatène et écrit sur disque
    self.deleted_data = pd.concat([old_deleted, deleted], ignore_index=True)
    self.deleted_data.to_csv(deleted_file_path, index=False)

    # Supprime dans le DataFrame principal
    self.data = self.data.drop(self.data.index[self.selected_indices]).reset_index(drop=True)

    # Vide la sélection et réaffiche la même tranche
    self.selected_indices = []
    self.display_scatter_plot()

# def delete_selected_points(self):
#     if not self.selected_indices:
#         messagebox.showwarning("Suppression", "Aucun point sélectionné à supprimer.")
#         return

#     # Vérifier que les indices sélectionnés sont bien dans la plage de self.current_slice_indices
#     valid_selected = [i for i in self.selected_indices if 0 <= i < len(self.current_slice_indices)]
#     if not valid_selected:
#         messagebox.showwarning("Suppression", "Aucun point sélectionné valide.")
#         return

#     global_indices = [self.current_slice_indices[i] for i in valid_selected]
    
#     # Vérifier que ces indices existent dans self.data
#     if any(idx not in self.data.index for idx in global_indices):
#         messagebox.showwarning("Suppression", "Certains points sélectionnés ne sont pas valides.")
#         return

#     previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
#     self.history.append((self.data.copy(), previous_deleted))

#     deleted = self.data.loc[global_indices]

#     deleted_file_path = os.path.splitext(self.file_path)[0] + "_deleted.csv"
#     if os.path.exists(deleted_file_path) and os.path.getsize(deleted_file_path) > 0:
#         try:
#             old_deleted = pd.read_csv(deleted_file_path)
#         except pd.errors.EmptyDataError:
#             old_deleted = pd.DataFrame()
#     else:
#         old_deleted = pd.DataFrame()

#     self.deleted_data = pd.concat([old_deleted, deleted], ignore_index=True)
#     self.deleted_data.to_csv(deleted_file_path, index=False)

#     # Suppression des points du dataframe principal
#     self.data = self.data.drop(index=global_indices).reset_index(drop=True)

#     # Réinitialiser la sélection
#     self.selected_indices = []
#     self.display_scatter_plot()

def clear_data(self):
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
    if self.history:
        self.data, self.deleted_data = self.history.pop()
        self.display_scatter_plot()
        deleted_file_path = os.path.splitext(self.file_path)[0] + "_deleted.csv"
        self.deleted_data.to_csv(deleted_file_path, index=False)
    else:
        messagebox.showwarning("Annulation", "Aucune action à annuler.")

def undo_all(self):
    if self.history:
        self.data, self.deleted_data = self.history[0]
        self.history = []
        self.display_scatter_plot()
    else:
        messagebox.showwarning("Annulation", "Aucune action à annuler.")

def open_multiplier_window(self):
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

def invalidate_series(self):
    if self.data is not None:
        self.data = None
    else:
        messagebox.showwarning("Invalidation", "Aucune donnée disponible")

def show_statistics(self):
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
    messagebox.showinfo(
        "À propos",
        "ClearCCNData v1.0\n\nApplication de visualisation de données environnementales.\nDéveloppée par :\nFanny Barcelo \nGhodbane Nour Elhouda \nMa-ida Salifou-Bawa \nSilas Teuliere."
    )   

def zoom_plot(self, factor):
        if not hasattr(self, 'ax') or self.ax is None:
            return

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        xcenter = (xlim[0] + xlim[1]) / 2
        ycenter = (ylim[0] + ylim[1]) / 2

        xwidth = (xlim[1] - xlim[0]) * factor / 2
        yheight = (ylim[1] - ylim[0]) * factor / 2

        self.ax.set_xlim([xcenter - xwidth, xcenter + xwidth])
        self.ax.set_ylim([ycenter - yheight, ycenter + yheight])

        self.canvas_widget.draw_idle()

def highlight_points(self, indices):
    if self.highlight:
        self.highlight.remove()
    self.selected_indices = [self.current_slice_indices[i] for i in indices]
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

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        # x = self.data['datetime'].to_numpy()
        # y = self.data['ccn_conc'].to_numpy()
        x = self.current_slice['datetime'].to_numpy()
        y = self.current_slice['ccn_conc'].to_numpy()

        norm_x_click = (event.mouseevent.xdata - xlim[0]) / (xlim[1] - xlim[0])
        norm_y_click = (event.mouseevent.ydata - ylim[0]) / (ylim[1] - ylim[0])
        norm_x = (mdates.date2num(x) - xlim[0]) / (xlim[1] - xlim[0])
        norm_y = (y - ylim[0]) / (ylim[1] - ylim[0])

        distances = np.hypot(norm_x - norm_x_click, norm_y - norm_y_click)
        
        print(f"Souris abscisse X = {event.mouseevent.xdata}, concertis en mdate = {mdates.date2num(event.mouseevent.xdata)}")
        print(f"Souris ordonnée Y = {event.mouseevent.ydata}")
        idx = np.argmin(distances)
        global_idx = self.current_slice_indices[idx] 

        print(f"Point sélectionné : ({x[idx]}, {y[idx]})")
        self.highlight_points([idx]) 
        self.selected_indices = [global_idx]
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
    max_date = self.data["datetime"].max()
    if self.current_start_date + timedelta(days=self.display_window_days) < max_date:
        self.current_start_date += timedelta(days=self.display_window_days)
        self.display_scatter_plot()

def previous_slice(self):
    min_date = self.data["datetime"].min()
    if self.current_start_date - timedelta(days=self.display_window_days) >= min_date:
        self.current_start_date -= timedelta(days=self.display_window_days)
        self.display_scatter_plot()

def display_scatter_plot(self):
    if self.data is None:
        return
    if "datetime" not in self.data.columns or "ccn_conc" not in self.data.columns:
        messagebox.showwarning("Visualisation", "Colonnes 'datetime' et 'ccn_conc' requises")
        return

    self.data["datetime"] = pd.to_datetime(self.data["datetime"], errors='coerce')
    self.data = self.data.dropna(subset=["datetime", "ccn_conc"])

    # Initialisation de la pagination si non définie
    if not hasattr(self, "display_window_days"):
        self.display_window_days = 0.25

    if not hasattr(self, "current_start_date") or self.current_start_date is None:
        self.current_start_date = self.data["datetime"].min()

    end_date = self.current_start_date + timedelta(days=self.display_window_days)
    data_slice = self.data[(self.data["datetime"] >= self.current_start_date) & 
                           (self.data["datetime"] < end_date)]

    self.x_floats = mdates.date2num(data_slice["datetime"])
    self.y_vals = data_slice["ccn_conc"].to_numpy()

    # NE PAS reset_index pour garder les indices originaux dans self.data
    self.current_slice = data_slice.copy()
    self.current_slice_indices = list(data_slice.index)  # indices globaux dans self.data

    for widget in self.inner_frame.winfo_children():
        widget.destroy()

    num_points = len(data_slice)
    height = max(20, num_points/500)
    fig = Figure(figsize=(height, 15))
    self.ax = fig.add_subplot(111)
    fig.tight_layout()

    colors = data_slice["ccn_sursaturation"].map({
        0.1: "purple",
        0.2: "blue",
        0.3: "green",
        0.4: "yellow",
        0.5: "red"
    }).fillna("gray")

    self.scatter_points = self.ax.scatter(
        data_slice["datetime"],
        data_slice["ccn_conc"],
        c=colors,
        alpha=0.5,
        picker=True
    )

    self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))
    self.ax.xaxis.set_major_locator(MaxNLocator(min(1000, max(10, num_points / 500))))

    self.ax.set_title(f"Affichage du {self.current_start_date.date()} au {end_date.date()}")
    self.ax.grid(True)
    fig.autofmt_xdate(rotation=45)
    fig.subplots_adjust(bottom=0.25)

    self.canvas_widget = FigureCanvasTkAgg(fig, master=self.inner_frame)
    self.canvas_widget.draw()
    self.canvas_widget.get_tk_widget().pack(fill=tk.X, expand=True)
    self.canvas_widget.mpl_connect('pick_event', self.on_click)

    if hasattr(self, 'rs') and self.rs is not None:
        self.rs.set_active(False)
        del self.rs

    self.selector = rectangle_selector.ManualRectangleSelector(
        self.ax,
        self.canvas_widget,
        data_slice,
        self.on_rectangle_select
    )