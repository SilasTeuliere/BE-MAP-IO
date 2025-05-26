import pytest
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from src.Gui.rectangle_selector import ManualRectangleSelector

class DummyEvent:
    def __init__(self, xdata, ydata, inaxes):
        self.xdata = xdata
        self.ydata = ydata
        self.inaxes = inaxes

@pytest.fixture
def setup_selector():
    fig, ax = plt.subplots()
    canvas = fig.canvas

    # Créer un DataFrame simulé avec datetime et ccn_conc
    import pandas as pd
    dates = pd.date_range("2024-01-01", periods=5)
    ccn_values = [10, 20, 30, 40, 50]
    data = pd.DataFrame({"datetime": dates, "ccn_conc": ccn_values})

    selected_indices = []
    def on_select_callback(indices):
        selected_indices.clear()
        selected_indices.extend(indices)

    selector = ManualRectangleSelector(ax, canvas, data, on_select_callback)
    yield selector, ax, canvas, selected_indices

def test_initial_state(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    assert selector.start_point is None
    assert selector.current_rect_patch is None
    assert selected_indices == []

def test_on_press_sets_start_point_and_removes_rect(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    event = DummyEvent(xdata=1, ydata=2, inaxes=ax)

    # Simuler un rectangle déjà dessiné
    from matplotlib.patches import Rectangle
    selector.current_rect_patch = Rectangle((0,0), 1, 1)
    ax.add_patch(selector.current_rect_patch)

    selector.on_press(event)
    assert selector.start_point == (1, 2)
    assert selector.current_rect_patch is None

def test_on_press_ignores_outside_axis(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    event = DummyEvent(xdata=1, ydata=2, inaxes=None)
    selector.on_press(event)
    assert selector.start_point is None

def test_on_motion_draws_rectangle_and_updates_bounds(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    selector.start_point = (1, 2)

    # Premier mouvement crée un patch
    event1 = DummyEvent(xdata=3, ydata=4, inaxes=ax)
    selector.on_motion(event1)
    assert selector.current_rect_patch is not None
    bounds = selector.current_rect_patch.get_bbox().bounds
    assert bounds[0] == 1  # xmin
    assert bounds[1] == 2  # ymin
    assert bounds[2] == 2  # largeur
    assert bounds[3] == 2  # hauteur

    # Second mouvement met à jour le rectangle
    event2 = DummyEvent(xdata=4, ydata=3, inaxes=ax)
    selector.on_motion(event2)
    bounds = selector.current_rect_patch.get_bbox().bounds
    assert bounds[0] == 1
    assert bounds[1] == 2
    assert bounds[2] == 3
    assert bounds[3] == 1

def test_on_motion_ignores_if_no_start_or_outside_axis(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    event_no_start = DummyEvent(xdata=3, ydata=4, inaxes=ax)
    selector.on_motion(event_no_start)  # start_point is None, should ignore
    assert selector.current_rect_patch is None

    selector.start_point = (1, 2)
    event_outside = DummyEvent(xdata=3, ydata=4, inaxes=None)
    selector.on_motion(event_outside)
    # Should not create patch
    assert selector.current_rect_patch is None

def test_on_release_calls_callback_with_correct_indices(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    selector.start_point = (mdates.date2num(selector.data['datetime'][1]), 15)
    event = DummyEvent(xdata=mdates.date2num(selector.data['datetime'][3]), ydata=45, inaxes=ax)

    # Simuler qu'on a dessiné un rectangle
    selector.current_rect_patch = None

    selector.on_release(event)
    # Indices sélectionnés doivent correspondre aux points entre datetime[1] et datetime[3], valeurs entre 15 et 45
    # C'est les indices 1, 2, 3
    assert selected_indices == [1, 2, 3]
    assert selector.current_rect_patch is None
    assert selector.start_point is None

def test_on_release_no_selection_prints_message(capfd, setup_selector):
    selector, ax, canvas, selected_indices = setup_selector
    selector.start_point = (mdates.date2num(selector.data['datetime'][0]), 0)
    event = DummyEvent(xdata=mdates.date2num(selector.data['datetime'][0]), ydata=5, inaxes=ax)
    selector.on_release(event)
    out, err = capfd.readouterr()
    assert "Aucun point sélectionné." in out
    assert selected_indices == []

def test_on_release_ignores_if_no_start_or_outside_axis(setup_selector):
    selector, ax, canvas, selected_indices = setup_selector

    event_no_start = DummyEvent(xdata=1, ydata=2, inaxes=ax)
    selector.on_release(event_no_start)  # start_point is None, ignore, no callback
    assert selected_indices == []

    selector.start_point = (1, 2)
    event_outside = DummyEvent(xdata=1, ydata=2, inaxes=None)
    selector.on_release(event_outside)
    assert selected_indices == []
