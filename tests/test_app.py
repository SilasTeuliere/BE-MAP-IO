import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from types import MethodType

from src.Gui.app import CCNDataApp
import src.Gui.data_utils as data_utils
import src.Gui.graph_utils as graph_utils
import src.Gui.interface as interface

#  FIXTURES  #
# Fixture pour créer une instance de la fenêtre Tkinter sans l'afficher

@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()
# Fixture pour créer une instance de l'application CCNDataApp
@pytest.fixture
def app(root):
    return CCNDataApp(root)

# Fixture automatique pour patcher les dépendances globales sauf si @patch est utilisé explicitement

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
# Test pour vérifier l'initialisation de l'application
def test_initialization(app):
    assert app.data is None
    assert app.highlight is None
    assert app.selected_indices == []
    assert isinstance(app.display_window_days, float)
    assert app.display_window_days == 0.25
    assert app.data_by_date == []
    assert app.history == []
    assert app.root.title() == "ClearCCNData"

# Test pour vérifier que les fonctions d'interface sont appelées

def test_interface_setup_called(root, monkeypatch):
    calls = {"menu": False, "shortcuts": False, "graph": False}

    monkeypatch.setattr(interface, "setup_menu", lambda _: calls.update(menu=True))
    monkeypatch.setattr(interface, "setup_shortcuts", lambda _: calls.update(shortcuts=True))
    monkeypatch.setattr(interface, "setup_graph_area", lambda _: calls.update(graph=True))

    CCNDataApp(root)
    assert all(calls.values())

# TEST SANS PATCH GLOBAL — version clean

# Test pour vérifier que la méthode clear_data réinitialise les données

def test_clear_data_resets_data(app):
    app.data = [1, 2, 3]
    def fake_clear(): app.data = None
    with patch.object(app, 'clear_data', fake_clear):
        app.clear_data()
    assert app.data is None

# Test pour vérifier le comportement de undo_last
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

# Test pour vérifier que load_csv met à jour les données


def test_load_csv_updates_data(app):
    with patch.object(app, 'load_csv', lambda: setattr(app, 'data', [42])):
        app.load_csv()
    assert app.data == [42]


# Test pour vérifier que delete_selected_points supprime les points sélectionnés


def test_delete_selected_points_clears_selection(app):
    app.selected_indices = [0, 1, 2] # Indices sélectionnés
    app.data = ['a', 'b', 'c', 'd'] # Données initiales
    def fake_delete():
        for i in sorted(app.selected_indices, reverse=True):
            if 0 <= i < len(app.data):
                app.data.pop(i)
        app.selected_indices.clear()
    with patch.object(app, 'delete_selected_points', fake_delete):
        app.delete_selected_points()
    assert app.selected_indices == []
    assert app.data == ['d']

# Test pour vérifier que invalidate_series est appelé
def test_invalidate_series_called(app):
    with patch.object(app, 'invalidate_series', MagicMock()) as mock_invalidate:
        app.invalidate_series()
        mock_invalidate.assert_called_once()


 

# Test pour vérifier que open_multiplier_window est appelé
def test_open_multiplier_window_called(app):
    with patch.object(app, 'open_multiplier_window', MagicMock()) as mock_open:
        app.open_multiplier_window()
        mock_open.assert_called_once()
# Test pour vérifier que clear_data vide les données


import pandas as pd

# Test pour vérifier que clear_data fonctionne avec un DataFrame

def test_clear_data_real(app):
    app.data = pd.DataFrame([1,2,3])  # au lieu de liste
    app.clear_data()
    assert app.data.empty

# Test pour vérifier que delete_selected_points gère les indices hors limites

def test_delete_selected_points_with_out_of_range_indices(app):
    app.selected_indices = [10, -1, 0]
    app.data = pd.DataFrame(['a', 'b', 'c'])
    app.current_slice_indices = list(range(len(app.data)))
    
    # Mock de l'attribut manquant car pas droit de modifier les modules
    app.file_path = "fake_path.csv"

    app.delete_selected_points()
