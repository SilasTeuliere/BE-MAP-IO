import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest
from src.Gui.graph_utils import (
    delete_selected_points,
    zoom_plot,
    highlight_points
)

# Dummy class pour simuler self
class DummySelf:
    def __init__(self):
        self.data = pd.DataFrame({
            'datetime': pd.date_range('2025-01-01', periods=5, freq='2D'),
            'ccn_conc': [10, 20, 30, 40, 50]
        })
        self.selected_indices = []
        self.current_slice_indices = []
        self.deleted_data = pd.DataFrame()
        self.history = []
        self.file_path = ""
        self.ax = MagicMock()
        self.canvas_widget = MagicMock()
        self.highlight = None
        self.current_slice = pd.DataFrame()

    def display_scatter_plot(self):
        # juste un stub, pour pas que ça plante en test
        pass
    def delete_selected_points(self):
        delete_selected_points(self)

    def zoom_plot(self, factor):
        zoom_plot(self, factor)

    def highlight_points(self, indices):
        highlight_points(self, indices)


# Tests pour delete_selected_points
def test_delete_selected_points(tmp_path):
    obj = DummySelf()
    deleted_path = tmp_path / "test_deleted.csv"
    obj.file_path = str(tmp_path / "test.csv")
    obj.selected_indices = [1, 3]
    obj.current_slice_indices = [0, 1, 2, 3, 4]

    with patch('pandas.read_csv', side_effect=FileNotFoundError):
        delete_selected_points(obj)

    
    assert list(obj.data.index) == [0, 1, 2]
    assert all(i not in obj.data.index for i in [1, 3]) is False  # on a reset l'index donc [1,3] != [1,3] maintenant

#
def test_delete_then_undo(tmp_path):
    fake_self = DummySelf()
    data = pd.DataFrame({'datetime': pd.date_range('2023-01-01', periods=3),
                         'ccn_conc': [10, 20, 30]})
    fake_self.data = data.copy()
    fake_self.current_slice_indices = list(range(3))
    fake_self.selected_indices = [1]
    fake_self.file_path = tmp_path / "test.csv"
    fake_self.history = []
    fake_self.deleted_data = pd.DataFrame()
    fake_self.display_scatter_plot = MagicMock()

    # Juste tester quer rien ne crash pas
    fake_self.delete_selected_points()
    assert len(fake_self.data) == 2


def test_delete_selected_points_invalid_indices():
    fake_self = DummySelf()
    fake_self.selected_indices = [100]  # Out of range
    fake_self.current_slice_indices = [0, 1, 2]
    with patch('tkinter.messagebox.showwarning') as mock_warn:
        fake_self.delete_selected_points()
        mock_warn.assert_called_once()


def test_zoom_plot_no_ax():
    fake_self = DummySelf()
    fake_self.ax = None
    fake_self.zoom_plot(0.5)  


def test_highlight_points_no_highlight():
    fake_self = DummySelf()
    fake_self.current_slice = pd.DataFrame({
        'datetime': pd.date_range('2023-01-01', periods=3),
        'ccn_conc': [1, 2, 3]
    })
    fake_self.highlight = None
    fake_self.highlight_points([0, 1])  

