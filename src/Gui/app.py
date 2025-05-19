import types
from . import interface
from .graph_utils import * 
from .data_utils import *

class CCNDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClearCCNData")
        self.data = None
        self.highlight = None
        self.selected_indices = []
        self.history = []
        self.current_start_date = None
        self.data_by_date = []
        self.display_window_days = 0.25

        interface.setup_menu(self)
        interface.setup_shortcuts(self)
        interface.setup_graph_area(self)

        self.load_csv = types.MethodType(load_csv, self)
        self.save_csv = types.MethodType(save_csv, self)

        self.on_click = types.MethodType(on_click, self)
        self.highlight_points = types.MethodType(highlight_points, self)
        self.delete_selected_points = types.MethodType(delete_selected_points, self)
        self.clear_data = types.MethodType(clear_data, self)
        self.undo_last = types.MethodType(undo_last, self)
        self.undo_all = types.MethodType(undo_all, self)
        self.open_multiplier_window = types.MethodType(open_multiplier_window, self)
        self.invalidate_series = types.MethodType(invalidate_series, self)
        self.show_statistics = types.MethodType(show_statistics, self)
        self.show_shortcuts = types.MethodType(show_shortcuts, self)
        self.show_about = types.MethodType(show_about, self)
        self.zoom_plot = types.MethodType(zoom_plot, self)
        self.on_select = types.MethodType(on_select, self)
        self.clear_selection = types.MethodType(clear_selection, self)
        self.on_rectangle_select = types.MethodType(on_rectangle_select, self)
        self.display_scatter_plot = types.MethodType(display_scatter_plot, self)
        self.next_slice = types.MethodType(next_slice, self)
        self.previous_slice = types.MethodType(previous_slice, self)
        self.add_color_legend = types.MethodType(add_color_legend, self)
        self.create_logical_pages = types.MethodType(create_logical_pages, self)
        self.on_scroll_zoom = types.MethodType(on_scroll_zoom, self)