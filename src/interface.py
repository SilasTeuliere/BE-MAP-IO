import tkinter as tk
from tkinter import ttk


def show_shortcuts():
    # Créer une fenêtre personnalisée
    shortcut_window = tk.Toplevel()
    shortcut_window.title("Raccourcis clavier")
    shortcut_window.geometry("900x300")

    # Créer un widget Text pour afficher les raccourcis
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

    # Créer un widget Text pour afficher les raccourcis
    text_widget = tk.Text(shortcut_window, wrap=tk.WORD, font=("Arial", 12), padx=10, pady=10)
    text_widget.pack(expand=True, fill=tk.BOTH)

    # Appliquer le style en gras à la partie avant les deux-points
    text_widget.tag_configure("bold", font=("Arial", 12, "bold"))

    # Ajouter les raccourcis dans le widget Text
    for line in shortcuts.split("\n"):
        if line:  # Vérifier si la ligne n'est pas vide
            # Séparer chaque ligne en deux parties : avant et après les deux-points
            before_colon, after_colon = line.split(":", 1)
            
            # Insérer la partie avant les deux-points en gras
            text_widget.insert(tk.END, before_colon, "bold")
            text_widget.insert(tk.END, " :")
            
            # Insérer la partie après les deux-points normalement
            text_widget.insert(tk.END, after_colon + "\n")

    # Ajouter un bouton de fermeture
    close_button = tk.Button(shortcut_window, text="Ok", command=shortcut_window.destroy)
    close_button.pack(pady=10)

    # Désactiver l'édition du widget Text
    text_widget.config(state=tk.DISABLED)


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
    edit_menu.add_separator()
    edit_menu.add_command(label="Rajouter coefficient multiplicateur à toutes les données")
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

    # L'ajout du logo 
    root.iconphoto(False, tk.PhotoImage(file="../data/logo.png"))
    
    create_menu(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()