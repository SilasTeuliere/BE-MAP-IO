import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk

from Gui.app import CCNDataApp
from Gui.graph_utils import delete_selected_points
from Gui.graph_utils import clear_selection, next_slice, previous_slice
from Gui.graph_utils import go_first, go_to_previous_day, go_to_page, go_to_next_day, go_last, update_page_display

def main():
    root = tk.Tk()
    root.title("ClearCCNData")
    root.geometry("900x700")

    logo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'logo.png')
    root.iconphoto(False, tk.PhotoImage(file=logo_path))

    app = CCNDataApp(root)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    select_button = tk.Button(button_frame, text="Désélectionner données", width=20, command=lambda: clear_selection(app))
    delete_button = tk.Button(button_frame, text="Supprimer données", width=20, command=lambda: delete_selected_points(app))

    prev_button = tk.Button(button_frame, text="⟵ Précédent", command=lambda: previous_slice(app))
    next_button = tk.Button(button_frame, text="Suivant ⟶", command=lambda: next_slice(app))
    start_button = tk.Button(button_frame, text="⏮ Début", command=lambda: go_first(app))
    day_prev_button = tk.Button(button_frame, text="◀ Jour précédent", command=lambda: go_to_previous_day(app))
    go_to_page_button = tk.Button(button_frame, text="Choix page", command=lambda: go_to_page(app))
    day_next_button = tk.Button(button_frame, text="Jour suivant ▶", command=lambda: go_to_next_day(app))
    end_button = tk.Button(button_frame, text="⏭ Fin", command=lambda: go_last(app))
    

    start_button.grid(row=0, column=0, padx=10)
    day_prev_button.grid(row=0, column=1, padx=10)
    prev_button.grid(row=0, column=2, padx=10)
    select_button.grid(row=0, column=3, padx=10)
    go_to_page_button.grid(row=0, column=4, padx=10)
    delete_button.grid(row=0, column=5, padx=10)
    next_button.grid(row=0, column=6, padx=10)
    day_next_button.grid(row=0, column=7, padx=10)
    end_button.grid(row=0, column=8, padx=10)

    app.prev_button = prev_button
    app.next_button = next_button
    app.start_button = start_button
    app.day_prev_button = day_prev_button
    app.go_to_page_button = go_to_page_button
    app.day_next_button = day_next_button
    app.end_button = end_button
    
    app.start_button.config(state="disabled")
    app.day_prev_button.config(state="disabled")
    app.prev_button.config(state="disabled")
    app.go_to_page_button.config(state="disabled")
    app.next_button.config(state="disabled")
    app.day_next_button.config(state="disabled")
    app.end_button.config(state="disabled")

    root.mainloop()

if __name__ == "__main__":
    main()