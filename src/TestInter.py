import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Toplevel, scrolledtext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import RectangleSelector
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import date2num
import numpy as np
import matplotlib.dates as mdates
import pandas as pd
import platform
import os
from data_loader import load_data

class CCNDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClearCCNData")
        self.data = None
        self.highlight = None
        self.create_menu()
        self.create_interface()
        self.bind_shortcuts()
        self.selected_indices = []
        self.history = []
        

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Importer un fichier CSV", command=self.load_csv, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_csv, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Supprimer toutes les données", command=self.clear_data, accelerator="Ctrl+U")
        edit_menu.add_command(label="Supprimer données sélectionnées", command=self.delete_selected_points, accelerator="Ctrl+X")
        edit_menu.add_command(label="Annuler toutes les modifications", command=self.undo_all, accelerator="Ctrl+Shift+Z")
        edit_menu.add_command(label="Annuler la dernière modification", command=self.undo_last, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rajouter coefficient multiplicateur", command=self.open_multiplier_window, accelerator="Ctrl+P")
        edit_menu.add_command(label="Invalider toute la série de données", command=self.invalidate_series, accelerator="Ctrl+I")
        menu_bar.add_cascade(label="Édition", menu=edit_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Statistiques", command=self.show_statistics, accelerator="Ctrl+A")
        menu_bar.add_cascade(label="Affichage", menu=view_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Raccourcis clavier", command=self.show_shortcuts)
        menu_bar.add_cascade(label="Aide", menu=help_menu)

        propo_menu = tk.Menu(menu_bar, tearoff=0)
        propo_menu.add_command(label="A propos", command=self.show_about)
        menu_bar.add_cascade(label="Information", menu=propo_menu)

        self.root.config(menu=menu_bar)

    def bind_shortcuts(self):
        modifier = "Command" if platform.system() == "Darwin" else "Control"
        self.root.bind_all(f"<{modifier}-o>", lambda event: self.load_csv())
        self.root.bind_all(f"<{modifier}-s>", lambda event: self.save_csv())
        self.root.bind_all(f"<{modifier}-u>", lambda event: self.clear_data())
        self.root.bind_all(f"<{modifier}-z>", lambda event: self.undo_last())
        self.root.bind_all(f"<{modifier}-x>", lambda event: self.delete_selected_points())
        self.root.bind_all(f"<{modifier}-Shift-Z>", lambda event: self.undo_all())
        self.root.bind_all(f"<{modifier}-p>", lambda event: self.open_multiplier_window())
        self.root.bind_all(f"<{modifier}-i>", lambda event: self.invalidate_series())
        self.root.bind_all(f"<{modifier}-a>", lambda event: self.show_statistics())
        self.root.bind_all(f"<{modifier}-minus>", lambda event: self.zoom_plot(1.2))  # Ctrl + -
        self.root.bind_all(f"<{modifier}-plus>", lambda event: self.zoom_plot(0.8))   # Ctrl + +
        self.root.bind_all(f"<{modifier}-equal>", lambda event: self.zoom_plot(0.8))  # Ctrl + = (pour les claviers sans pavé)

    def create_interface(self):
        self.graph_frame = tk.Frame(self.root, bd=2, relief="ridge")
        self.graph_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.scrollbar_x = tk.Scrollbar(self.graph_frame, orient="horizontal")
        self.scrollbar_y = tk.Scrollbar(self.graph_frame, orient="vertical")

        self.canvas = tk.Canvas(self.graph_frame, bg="white", xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_x.config(command=self.canvas.xview)
        self.scrollbar_y.config(command=self.canvas.yview)

        self.scrollbar_x.pack(side="bottom", fill="x")
        self.scrollbar_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.data = load_data(file_path)
            if self.data is None:
                messagebox.showwarning("Chargement", "Échec du chargement des données")
                return
            messagebox.showinfo("Chargement", "Fichier chargé avec succès")
        self.display_scatter_plot()

    def save_csv(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                # Enregistrement du fichier principal
                self.data.to_csv(file_path, index=False)
                self.file_path = file_path  # Met à jour le chemin pour les suppressions futures

                # Enregistrement du fichier supprimé
                deleted_file_path = os.path.splitext(file_path)[0] + "_deleted.csv"
                if hasattr(self, 'deleted_data') and not self.deleted_data.empty:
                    self.deleted_data.to_csv(deleted_file_path, index=False)
        else:
            messagebox.showwarning("Sauvegarde", "Aucune donnée à sauvegarder")

    def delete_selected_points(self):
        if not self.selected_indices:
            messagebox.showwarning("Suppression", "Aucun point sélectionné à supprimer.")
            return
        # Sauvegarder l'état actuel dans l'historique pour permettre l'annulation
        previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
        self.history.append((self.data.copy(), previous_deleted))

        # Récupérer les points à supprimer
        deleted = self.data.iloc[self.selected_indices]

        # Déterminer le chemin du fichier de suppression
        deleted_file_path = os.path.splitext(self.file_path)[0] + "_deleted.csv"

        # Charger l'existant si le fichier supprimé n'est pas vide
        if os.path.exists(deleted_file_path) and os.path.getsize(deleted_file_path) > 0:
            try:
                old_deleted = pd.read_csv(deleted_file_path)
            except pd.errors.EmptyDataError:
                old_deleted = pd.DataFrame()
        else:
            old_deleted = pd.DataFrame()

        # Fusionner les anciennes et nouvelles suppressions
        self.deleted_data = pd.concat([old_deleted, deleted], ignore_index=True)

        # Supprimer les lignes du DataFrame principal
        self.data = self.data.drop(self.data.index[self.selected_indices]).reset_index(drop=True)

        # Réinitialiser la sélection et mettre à jour le graphique
        self.selected_indices = []
        self.display_scatter_plot()

    def clear_data(self):
        if self.data is not None and not self.data.empty:
            # Sauvegarde dans l'historique pour pouvoir annuler
            previous_deleted = getattr(self, 'deleted_data', pd.DataFrame()).copy()
            self.history.append((self.data.copy(), previous_deleted))

            # Vide les données
            self.data = self.data.iloc[0:0]  # Conserve les colonnes
            self.selected_indices = []

            # Vide aussi les données supprimées enregistrées si tu veux
            self.deleted_data = pd.DataFrame()

            # Met à jour l'affichage
            self.display_scatter_plot()
        else:
            messagebox.showwarning("Suppression", "Aucune donnée à supprimer")
            

    def undo_last(self):
        if self.history:
            self.data, self.deleted_data = self.history.pop()
            self.display_scatter_plot()
            # Restaurer aussi le fichier des supprimés
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
                    self.data *= coeff
                    self.display_scatter_plot()
                    messagebox.showinfo("Coefficient", f"Multiplication effectuée avec {coeff}")
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

            # Nouvelle fenêtre
            stats_window = Toplevel()
            stats_window.title("Statistiques")
            stats_window.geometry("800x400")  # ← ici tu choisis la taille

            # Zone de texte avec ascenseur
            text_area = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD, font=("Courier", 10))
            text_area.pack(expand=True, fill='both')
            text_area.insert(tk.END, stats)
            text_area.config(state='disabled')  # Pour rendre le texte non modifiable

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

        # Calcul du centre
        xcenter = (xlim[0] + xlim[1]) / 2
        ycenter = (ylim[0] + ylim[1]) / 2

        # Appliquer le facteur de zoom
        xwidth = (xlim[1] - xlim[0]) * factor / 2
        yheight = (ylim[1] - ylim[0]) * factor / 2

        # Nouvelle zone
        self.ax.set_xlim([xcenter - xwidth, xcenter + xwidth])
        self.ax.set_ylim([ycenter - yheight, ycenter + yheight])

        self.canvas_widget.draw_idle()

    def highlight_points(self, indices):
        if self.highlight:
            self.highlight.remove()
        xdata = self.data['datetime'].iloc[indices]
        ydata = self.data['ccn_conc'].iloc[indices]
        self.highlight = self.ax.scatter(xdata, ydata, color='red', s=80, edgecolors='black', zorder=10)
        self.selected_indices = indices
        self.canvas_widget.draw_idle()

    def on_click(self, event):
        if event.mouseevent.button == 1 and event.artist == self.scatter_points:
            # Enregistrer les limites actuelles de l'axe
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            x = self.data['datetime'].to_numpy()
            y = self.data['ccn_conc'].to_numpy()
            #distances = np.hypot(mdates.date2num(x) - mdates.date2num(event.mouseevent.xdata), y - event.mouseevent.ydata)
            #distances = np.hypot(mdates.date2num(x) - event.mouseevent.xdata, y - event.mouseevent.ydata)
            
            # Convertir les coordonnées du clic et des points en coordonnées normalisées
            norm_x_click = (event.mouseevent.xdata - xlim[0]) / (xlim[1] - xlim[0])
            norm_y_click = (event.mouseevent.ydata - ylim[0]) / (ylim[1] - ylim[0])
            norm_x = (mdates.date2num(x) - xlim[0]) / (xlim[1] - xlim[0])
            norm_y = (y - ylim[0]) / (ylim[1] - ylim[0])

            # Calculer les distances normalisées
            distances = np.hypot(norm_x - norm_x_click, norm_y - norm_y_click)
            
            print(f"Souris abscisse X = {event.mouseevent.xdata}, concertis en mdate = {mdates.date2num(event.mouseevent.xdata)}")
            print(f"Souris ordonnée Y = {event.mouseevent.ydata}")
            idx = np.argmin(distances)
            print(f"Point sélectionné : ({x[idx]}, {y[idx]})")
            self.highlight_points([idx])

            # Restaurer les limites de l'axe
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas_widget.draw_idle()

    # def on_click(self, event):
    #     if event.inaxes == self.ax:
    #         x, y = event.xdata, event.ydata
    #         print(f"Clic détecté aux coordonnées : ({x}, {y})")

    # def on_select(self, eclick, erelease):
    #     xmin, xmax = sorted([eclick.xdata, erelease.xdata])
    #     ymin, ymax = sorted([eclick.ydata, erelease.ydata])

    #     x_num = mdates.date2num(self.data['datetime'])  # Convertit les dates en floats
    #     y = self.data['ccn_conc'].to_numpy()

    #     mask = (x_num >= xmin) & (x_num <= xmax) & (y >= ymin) & (y <= ymax)
    #     indices = self.data[mask].index.tolist()

    #     print(f"{len(indices)} points sélectionnés.")
    #     self.selected_indices = indices
    #     self.highlight_points(indices)


    def on_select(self, eclick, erelease):
        """Sélectionne tous les points dans le rectangle et les met en surbrillance."""
        if self.data is None:
            return

        # 1) Récupère les coins du rectangle en coordonnées data (float)
        xmin, xmax = sorted([eclick.xdata, erelease.xdata])
        ymin, ymax = sorted([eclick.ydata, erelease.ydata])

        # 2) Masque booléen sur les arrays
        mask = (
            (self.x_floats >= xmin) & (self.x_floats <= xmax) &
            (self.y_vals   >= ymin) & (self.y_vals   <= ymax)
        )

        # 3) Indices sélectionnés
        indices = np.nonzero(mask)[0].tolist()
        if not indices:
            messagebox.showinfo("Sélection", "Aucun point dans la zone.")
            return

        # 4) Stocke et affiche en rouge
        self.selected_indices = indices
        self.highlight_points(indices)
        print(f"{len(indices)} point(s) sélectionné(s) par rectangle.")

    def clear_selection(self):
        if self.highlight:
            self.highlight.remove()
            self.highlight = None
            self.canvas_widget.draw_idle()
        self.selected_indices = []

    def display_scatter_plot(self):
        if self.data is None:
            return
        if "datetime" not in self.data.columns or "ccn_conc" not in self.data.columns:
            messagebox.showwarning("Visualisation", "Colonnes 'datetime' et 'ccn_conc' requises")
            return

        # Conversion de la colonne datetime et nettoyage
        self.data["datetime"] = pd.to_datetime(self.data["datetime"], errors='coerce')
        self.data = self.data.dropna(subset=["datetime", "ccn_conc"])
        
        # Création des arrays nécessaires pour on_select
        self.x_floats = mdates.date2num(self.data["datetime"])
        self.y_vals = self.data["ccn_conc"].to_numpy()

        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        num_points = len(self.data)
        height = max(20, num_points/500)
        fig = Figure(figsize=(height, 15))
        self.ax = fig.add_subplot(111)
        fig.tight_layout()
        self.scatter_points = self.ax.scatter(self.data["datetime"], self.data["ccn_conc"], alpha=0.30, picker=True)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))

        # Utilisation de AutoDateLocator pour gérer automatiquement les graduations
        nombre_de_lignes = self.data.shape[0]
        self.ax.xaxis.set_major_locator(MaxNLocator(max(10, nombre_de_lignes))) #A changer peut etre plus tard

        self.ax.grid(True)
        fig.autofmt_xdate(rotation=45)
        fig.subplots_adjust(bottom=0.25)

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.inner_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.X, expand=True)

        # Connecter l'événement pick pour les clics sur les points
        self.canvas_widget.mpl_connect('pick_event', self.on_click)

        # Ajouter le RectangleSelector, actif dès l'affichage du scatter plot
        self.rs = RectangleSelector(
            self.ax, 
            self.on_select,
            button=[1],
            minspanx=5, 
            minspany=5, 
            spancoords='data',
            interactive=True
        )


def main():
    root = tk.Tk()
    root.title("ClearCCNData")
    root.geometry("800x600")

    logo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'logo.png')
    root.iconphoto(False, tk.PhotoImage(file=logo_path))

    app = CCNDataApp(root)

    # Cadre pour les boutons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    select_button = tk.Button(button_frame, text="Sélectionner données", width=20, command=app.clear_selection)
    delete_button = tk.Button(button_frame, text="Supprimer données", width=20, command=app.delete_selected_points)

    select_button.grid(row=0, column=0, padx=10)
    delete_button.grid(row=0, column=1, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()


# Prochaine fois :
# Regarder le probleme de taille du graphe 
# Regarder le probleme de selection des points
# Regarder le probleme de des dates sur la graphe  
# Faire la selection de plusieur point en meme temps