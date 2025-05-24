import tkinter as tk
import platform

from .data_utils import load_csv, save_csv
from .graph_utils import clear_data, delete_selected_points, undo_all, undo_last, open_multiplier_window, invalidate_series
from .graph_utils import show_about, show_shortcuts, show_statistics

def setup_menu(self):
    menu_bar = tk.Menu(self.root, tearoff=0)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Importer un fichier CSV", command=lambda: load_csv(self), accelerator="Ctrl+O")
    file_menu.add_command(label="Sauvegarder", command=lambda: save_csv(self), accelerator="Ctrl+S")
    file_menu.add_separator()
    file_menu.add_command(label="Quitter", command=self.root.quit)
    menu_bar.add_cascade(label="Fichier", menu=file_menu)

    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Supprimer toutes les données", command=lambda: clear_data(self), accelerator="Ctrl+U")
    edit_menu.add_command(label="Supprimer données sélectionnées", command=lambda: delete_selected_points(self), accelerator="Ctrl+X")
    edit_menu.add_command(label="Annuler toutes les modifications", command=lambda: undo_all(self), accelerator="Ctrl+Shift+Z")
    edit_menu.add_command(label="Annuler la dernière modification", command=lambda: undo_last(self), accelerator="Ctrl+Z")
    edit_menu.add_command(label="Rajouter coefficient multiplicateur", command=lambda: open_multiplier_window(self), accelerator="Ctrl+P")
    edit_menu.add_command(label="Supprimer page", command=lambda: invalidate_series(self), accelerator="Ctrl+I")
    menu_bar.add_cascade(label="Édition", menu=edit_menu)

    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(label="Statistiques", command=lambda: show_statistics(self), accelerator="Ctrl+A")
    menu_bar.add_cascade(label="Affichage", menu=view_menu)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Raccourcis clavier", command=lambda: show_shortcuts(self))
    menu_bar.add_cascade(label="Aide", menu=help_menu)

    propo_menu = tk.Menu(menu_bar, tearoff=0)
    propo_menu.add_command(label="A propos", command=lambda: show_about(self))
    menu_bar.add_cascade(label="Information", menu=propo_menu)

    self.root.config(menu=menu_bar)

def setup_shortcuts(self):
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

def setup_graph_area(self):
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