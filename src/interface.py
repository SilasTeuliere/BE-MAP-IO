import tkinter as tk
from tkinter import ttk , messagebox
import os


def show_shortcuts():

    shortcut_window = tk.Toplevel()
    shortcut_window.title("Raccourcis clavier")
    shortcut_window.geometry("900x300")

    shortcuts = (
        "Importer un Fichier CSV : Ctrl + O / Cmd + O sur Mac\n"
        "Sauvegarder le fichier de flag :  Ctrl + S / Cmd + S sur Mac\n"
        "Supprimer l’ensemble des données  :  Ctrl + U / Cmd + U sur Mac\n"
        "Appliquer un coefficient multiplicateur à toutes les données :  Ctrl + P / Cmd + P sur Mac\n"
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

def open_multiplier_window():
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
            print(f"Coefficient entré : {coeff}") 
            multiplier_window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")
            coeff_entry.delete(0, tk.END)

    validate_button = tk.Button(multiplier_window, text="Valider", command=validate_multiplier)
    validate_button.pack(pady=10)

def create_menu(root):
    menubar = tk.Menu(root)
    
    # Menu Fichier
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Importer un fichier csv")
    file_menu.add_command(label="Sauvgarder un fichier")
    file_menu.add_separator()
    file_menu.add_command(label="Quitter", command=root.quit)
    menubar.add_cascade(label="Fichier", menu=file_menu)
    
    # Menu Edition
    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label="Supprimer toutes les données")
    edit_menu.add_command(label="Annuler toutes les modifications")
    edit_menu.add_command(label="Annuler la dernière modification")
    edit_menu.add_command(label="Rajouter coefficient multiplicateur à toutes les données", command=open_multiplier_window)
    edit_menu.add_command(label="Invalider toute la série de données")
    menubar.add_cascade(label="Édition", menu=edit_menu)
    
    # Menu Affichage
    view_menu = tk.Menu(menubar, tearoff=0)
    view_menu.add_command(label="Statistiques")
    view_menu.add_separator()
    menubar.add_cascade(label="Affichage", menu=view_menu)
    
    # Menu Aide
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="À propos")
    help_menu.add_command(label="Raccourcis clavier", command=show_shortcuts)
    menubar.add_cascade(label="Aide", menu=help_menu)
    
    root.config(menu=menubar)



def main():
    root = tk.Tk()
    root.title("ClearCCNData")
    root.geometry("800x600")

    logo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'logo.png')
    root.iconphoto(False, tk.PhotoImage(file=logo_path))
    
    create_menu(root)
    
    # Cadre principal pour afficher le graphe 
    graph_frame = tk.Frame(root, bd=2, relief="ridge")
    graph_frame.pack(expand=True, fill="both", padx=20, pady=20)

    canvas = tk.Canvas(graph_frame, bg="white")  # Ajout du fond blanc pour simuler un graphe
    canvas.pack(expand=True, fill="both")

    # Cadre pour les boutons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    select_button = tk.Button(button_frame, text="Sélectionner données", width=20)
    delete_button = tk.Button(button_frame, text="Supprimer données", width=20)

    select_button.grid(row=0, column=0, padx=10)
    delete_button.grid(row=0, column=1, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()