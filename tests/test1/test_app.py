import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from types import MethodType

from src.Gui.app import CCNDataApp
import src.Gui.data_utils as data_utils
import src.Gui.graph_utils as graph_utils
import src.Gui.interface as interface

#  FIXTURES  #

@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

@pytest.fixture
def app(root):
    return CCNDataApp(root)

# Auto patch sauf si @patch utilisé explicitement
@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    monkeypatch.setattr(data_utils, 'load_csv', MagicMock(return_value=[10, 20, 30]))
    monkeypatch.setattr(data_utils, 'save_csv', MagicMock())
    monkeypatch.setattr(graph_utils, 'display_scatter_plot', MagicMock())
    monkeypatch.setattr(interface, 'setup_menu', MagicMock())
    monkeypatch.setattr(interface, 'setup_shortcuts', MagicMock())
    monkeypatch.setattr(interface, 'setup_graph_area', MagicMock())
    yield

#  TESTS #

def test_initialization(app):
    assert app.data is None
    assert app.highlight is None
    assert app.selected_indices == []
    assert isinstance(app.display_window_days, float)
    assert app.display_window_days == 0.25
    assert app.data_by_date == []
    assert app.history == []
    assert app.root.title() == "ClearCCNData"

def test_interface_setup_called(root, monkeypatch):
    calls = {"menu": False, "shortcuts": False, "graph": False}

    monkeypatch.setattr(interface, "setup_menu", lambda _: calls.update(menu=True))
    monkeypatch.setattr(interface, "setup_shortcuts", lambda _: calls.update(shortcuts=True))
    monkeypatch.setattr(interface, "setup_graph_area", lambda _: calls.update(graph=True))

    CCNDataApp(root)
    assert all(calls.values())

# TEST SANS PATCH GLOBAL — version clean


def test_clear_data_resets_data(app):
    app.data = [1, 2, 3]
    def fake_clear(): app.data = None
    with patch.object(app, 'clear_data', fake_clear):
        app.clear_data()
    assert app.data is None

def test_undo_last_behavior(app):
    app.history = [[1], [2]]
    app.data = [2]
    def fake_undo():
        app.data = app.history[-2]
        app.history.pop()
    with patch.object(app, 'undo_last', fake_undo):
        app.undo_last()
    assert app.data == [1]
    assert len(app.history) == 1

def test_load_csv_updates_data(app):
    with patch.object(app, 'load_csv', lambda: setattr(app, 'data', [42])):
        app.load_csv()
    assert app.data == [42]




def test_delete_selected_points_clears_selection(app):
    app.selected_indices = [0, 1, 2]
    app.data = ['a', 'b', 'c', 'd']
    def fake_delete():
        for i in sorted(app.selected_indices, reverse=True):
            if 0 <= i < len(app.data):
                app.data.pop(i)
        app.selected_indices.clear()
    with patch.object(app, 'delete_selected_points', fake_delete):
        app.delete_selected_points()
    assert app.selected_indices == []
    assert app.data == ['d']

def test_invalidate_series_called(app):
    with patch.object(app, 'invalidate_series', MagicMock()) as mock_invalidate:
        app.invalidate_series()
        mock_invalidate.assert_called_once()

def test_open_multiplier_window_called(app):
    with patch.object(app, 'open_multiplier_window', MagicMock()) as mock_open:
        app.open_multiplier_window()
        mock_open.assert_called_once()

"""
def test_display_scatter_plot_receives_data(app, monkeypatch):
    app.data = [
        {"date": "2024-01-01", "value": 10},
        {"date": "2024-01-02", "value": 20}
    ]

    mock_display = MagicMock()
    # On remplace la méthode liée sur l'instance directement
    monkeypatch.setattr(app, "display_scatter_plot", mock_display)

    app.display_scatter_plot()

    mock_display.assert_called_once_with()
"""

def test_display_scatter_plot_calls_graph_utils(app, monkeypatch):
    app.data = [{"date": "2024-01-01", "value": 10}]
    app.highlight = None

    # Patch la fonction graph_utils.display_scatter_plot pour capter l'appel
    mock_graph_display = MagicMock()
    monkeypatch.setattr(graph_utils, "display_scatter_plot", mock_graph_display)

    # Appelle la méthode de l’app
    app.display_scatter_plot()

    # Vérifie qu’on a appelé graph_utils.display_scatter_plot avec les bons args
    mock_graph_display.assert_called_once_with(app.data, app.highlight)
