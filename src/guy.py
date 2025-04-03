import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import platform


class CCNDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClearCCNData")
        self.data = None
        self.create_menu()
        
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Importer un Fichier CSV", command=self.load_csv, accelerator=self.get_shortcut("O"))
        file_menu.add_command(label="Sauvegarder", command=self.save_csv, accelerator=self.get_shortcut("S"))
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Supprimer toutes les données", command=self.clear_data, accelerator=self.get_shortcut("U"))
        edit_menu.add_command(label="Annuler la dernière modification", command=self.undo_last, accelerator=self.get_shortcut("Z"))
        edit_menu.add_command(label="Annuler toutes les modifications", command=self.undo_all, accelerator=self.get_shortcut("Shift-Z"))
        edit_menu.add_command(label="Appliquer un coefficient", command=self.apply_coefficient, accelerator=self.get_shortcut("P"))
        edit_menu.add_command(label="Invalider toute la série", command=self.invalidate_series, accelerator=self.get_shortcut("I"))
        menu_bar.add_cascade(label="Édition", menu=edit_menu)
        
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Afficher les statistiques", command=self.show_statistics, accelerator=self.get_shortcut("A"))
        menu_bar.add_cascade(label="Affichage", menu=view_menu)
        
        self.root.config(menu=menu_bar)
        
        self.bind_shortcuts()

    def get_shortcut(self, key):
        if platform.system() == "Darwin":  # macOS
            return f"⌘{key}"
        else:  # Windows/Linux
            return f"Ctrl+{key}"

    #
    def bind_shortcuts(self):
        modifier = "Command" if platform.system() == "Darwin" else "Control"
        self.root.bind_all(f"<{modifier}-o>", lambda event: self.load_csv())
        self.root.bind_all(f"<{modifier}-s>", lambda event: self.save_csv())
        self.root.bind_all(f"<{modifier}-u>", lambda event: self.clear_data())
        self.root.bind_all(f"<{modifier}-z>", lambda event: self.undo_last())
        self.root.bind_all(f"<{modifier}-Shift-z>", lambda event: self.undo_all())
        self.root.bind_all(f"<{modifier}-p>", lambda event: self.apply_coefficient())
        self.root.bind_all(f"<{modifier}-i>", lambda event: self.invalidate_series())
        self.root.bind_all(f"<{modifier}-a>", lambda event: self.show_statistics())

    #Charge un fichier csv (Fini)
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.data = pd.read_csv(file_path)
            messagebox.showinfo("Chargement", "Fichier chargé avec succès")

        return self.diagramme_poster()

    #Affiche le diagramme en nuage de point (A finir)
    def diagramme_poster(self):
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        if len(numeric_cols) < 2:
            messagebox.showwarning("Visualisation", "Pas assez de colonnes numériques pour un graphique")
            return

        x_col, y_col = numeric_cols[:2]
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.scatter(self.data[x_col], self.data[y_col], alpha=0.5, label="Données")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title("Diagramme de points")
        ax.legend()
        ax.grid(True)
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    #Sauvegarde le fichier csv (A finir)
    def save_csv(self):
        if self.data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                self.data.to_csv(file_path, index=False)
                messagebox.showinfo("Sauvegarde", "Fichier sauvegardé avec succès")
        else:
            messagebox.showwarning("Sauvegarde", "Aucune donnée à sauvegarder")

    #Supprime toute les données (A faire)
    def clear_data(self):
        if self.data is not None:
            self.data = None
            messagebox.showinfo("Suppression", "Toutes les données ont été supprimées")
        else:
            messagebox.showwarning("Suppression", "Aucune donnée à supprimer")

    #Annule la derniere action (A faire)
    def undo_last(self):
        messagebox.showinfo("Annuler", "Dernière modification annulée")

    #Annuler toute les action (A faire)
    def undo_all(self):
        messagebox.showinfo("Annuler", "Toutes les modifications ont été annulées")

    #Applique un coefficient au donnée (A finir)
    def apply_coefficient(self):
        if self.data is not None:
            factor = 1.18
            self.data *= factor
            messagebox.showinfo("Modification", "Coefficient appliqué à toutes les données")
        else:
            messagebox.showwarning("Modification", "Aucune donnée disponible")

    #Supprime une série de donnée selectionner (A faire)
    def invalidate_series(self):
        if self.data is not None:
            self.data = None
            messagebox.showinfo("Invalidation", "Toute la série de données a été invalidée")
        else:
            messagebox.showwarning("Invalidation", "Aucune donnée disponible")

    #Affiche des statistiques descriptives sur les données chargées. (A peaufiner)
    def show_statistics(self):
        if self.data is not None:
            stats = self.data.describe()
            messagebox.showinfo("Statistiques", stats.to_string())
        else:
            messagebox.showwarning("Statistiques", "Aucune donnée disponible")

if __name__ == "__main__":
    root = tk.Tk()
    app = CCNDataApp(root)
    root.mainloop()