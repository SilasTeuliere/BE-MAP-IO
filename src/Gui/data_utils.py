import os
from tkinter import filedialog, messagebox
from .graph_utils import display_scatter_plot
from .graph_utils import create_logical_pages
from data_loader import load_data


def load_csv(self):
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        self.file_path = file_path
        print(f"Fichier sélectionné : {file_path}")
        print(f"Existe ? {os.path.exists(file_path)}")
        self.data = load_data(file_path)
        if self.data is None:
            messagebox.showwarning("Chargement", "Échec du chargement des données")
            return
    create_logical_pages(self)
    display_scatter_plot(self)

def save_csv(self):
    if self.data is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.data.to_csv(file_path, index=False)
            self.file_path = file_path

            deleted_file_path = os.path.splitext(file_path)[0] + "_deleted.csv"
            if hasattr(self, 'deleted_data') and not self.deleted_data.empty:
                self.deleted_data.to_csv(deleted_file_path, index=False)
    else:
        messagebox.showwarning("Sauvegarde", "Aucune donnée à sauvegarder")

