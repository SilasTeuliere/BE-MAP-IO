import tkinter as tk
from tkinter import filedialog
import platform
import csv

def save_file():
    filepath = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("Fichiers CSV", "*.csv"),
                                                       ("Tous les fichiers", "*.*")])
    if filepath:
        # Exemple de données à sauvegarder dans le CSV
        data = [["Nom", "Age", "Ville"],
                ["Alice", 30, "Paris"],
                ["Bob", 25, "Lyon"]]

        with open(filepath, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"Fichier CSV sauvegardé : {filepath}")

def load_file():
    filepath = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv"),
                                                    ("Tous les fichiers", "*.*")])
    if filepath:
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            content = list(reader)
        print(f"Fichier chargé : {filepath}\nContenu :")
        for row in content:
            print(row)

def setup_shortcuts(root):
    system = platform.system()
    shortcut_s = "<Command-s>" if system == "Darwin" else "<Control-s>"
    shortcut_o = "<Command-o>" if system == "Darwin" else "<Control-o>"

    root.bind(shortcut_s, lambda _: save_file())
    root.bind(shortcut_o, lambda _: load_file())

# Création de la fenêtre principale
app = tk.Tk()
app.title("Application CSV - Sauvegarde/Chargement")

setup_shortcuts(app)

tk.Label(app, text="Appuyez sur Ctrl+S pour sauvegarder (CSV)\nAppuyez sur Ctrl+O pour charger (CSV)").pack(padx=20, pady=20)

tk.Button(app, text="Sauvegarder CSV", command=save_file).pack(pady=10)
tk.Button(app, text="Charger CSV", command=load_file).pack(pady=10)

app.mainloop()
