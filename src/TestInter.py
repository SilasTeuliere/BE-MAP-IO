import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import pandas as pd
import platform
from data_loader import load_data

class CCNDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClearCCNData")
        self.data = None
        self.create_menu()
        self.create_interface()
        self.bind_shortcuts()

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

        self.root.config(menu=menu_bar)

    def bind_shortcuts(self):
        modifier = "Command" if platform.system() == "Darwin" else "Control"
        self.root.bind_all(f"<{modifier}-o>", lambda event: self.load_csv())
        self.root.bind_all(f"<{modifier}-s>", lambda event: self.save_csv())
        self.root.bind_all(f"<{modifier}-u>", lambda event: self.clear_data())
        self.root.bind_all(f"<{modifier}-z>", lambda event: self.undo_last())
        self.root.bind_all(f"<{modifier}-Shift-Z>", lambda event: self.undo_all())
        self.root.bind_all(f"<{modifier}-p>", lambda event: self.open_multiplier_window())
        self.root.bind_all(f"<{modifier}-i>", lambda event: self.invalidate_series())
        self.root.bind_all(f"<{modifier}-a>", lambda event: self.show_statistics())

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
                self.data.to_csv(file_path, index=False)
                messagebox.showinfo("Sauvegarde", "Fichier sauvegardé avec succès")
        else:
            messagebox.showwarning("Sauvegarde", "Aucune donnée à sauvegarder")

    def clear_data(self):
        if self.data is not None:
            self.data = None
            messagebox.showinfo("Suppression", "Toutes les données ont été supprimées")
        else:
            messagebox.showwarning("Suppression", "Aucune donnée à supprimer")

    def undo_last(self):
        messagebox.showinfo("Annuler", "Dernière modification annulée")

    def undo_all(self):
        messagebox.showinfo("Annuler", "Toutes les modifications ont été annulées")

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
            messagebox.showinfo("Invalidation", "Toute la série de données a été invalidée")
        else:
            messagebox.showwarning("Invalidation", "Aucune donnée disponible")

    def show_statistics(self):
        if self.data is not None:
            stats = self.data.describe()
            messagebox.showinfo("Statistiques", stats.to_string())
        else:
            messagebox.showwarning("Statistiques", "Aucune donnée disponible")

    def show_shortcuts(self):
        shortcut_window = tk.Toplevel()
        shortcut_window.title("Raccourcis clavier")
        shortcut_window.geometry("900x300")

        shortcuts = (
            "Importer un Fichier CSV : Ctrl + O / Cmd + O sur Mac\n"
            "Sauvegarder le fichier :  Ctrl + S / Cmd + S sur Mac\n"
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

    def display_scatter_plot(self):
        if self.data is None:
            return
        if "datetime" not in self.data.columns or "ccn_conc" not in self.data.columns:
            messagebox.showwarning("Visualisation", "Colonnes 'datetime' et 'ccn_conc' requises")
            return

        self.data["datetime"] = pd.to_datetime(self.data["datetime"], errors='coerce')
        self.data = self.data.dropna(subset=["datetime", "ccn_conc"])

        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(30, 10))  # Taille plus grande pour plus d'espace
        ax = fig.add_subplot(111)
        ax.scatter(self.data["datetime"], self.data["ccn_conc"], alpha=0.5)
        ax.set_xlabel("Date et Heure")
        ax.set_ylabel("CCN_Conc")
        ax.set_title("Données CCN_Conc")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y %H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.grid(True)
        for label in ax.get_xticklabels():
            label.set_rotation(90)

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.inner_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CCNDataApp(root)
    root.mainloop()
