import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk

from Gui.app import CCNDataApp
from Gui.graph_utils import delete_selected_points
from Gui.graph_utils import clear_selection

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

    select_button = tk.Button(button_frame, text="Désélectionner données", width=20, command=lambda: clear_selection(app))
    delete_button = tk.Button(button_frame, text="Supprimer données", width=20, command=lambda: delete_selected_points(app))

    select_button.grid(row=0, column=0, padx=10)
    delete_button.grid(row=0, column=1, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()