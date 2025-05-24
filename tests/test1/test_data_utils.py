import pytest
from unittest.mock import patch
import pandas as pd
from src.Gui import data_utils

class DummySelf:
    def __init__(self):
        self.data = None
        self.file_path = None
        self.deleted_data = pd.DataFrame({'a':[1, 2]})

@pytest.fixture
def dummy():
    return DummySelf()

@patch('src.Gui.data_utils.filedialog.askopenfilename', return_value='fake_path.csv')
@patch('src.Gui.data_utils.load_data', return_value=pd.DataFrame({'x':[1,2], 'y':[3,4]}))
@patch('src.Gui.data_utils.create_logical_pages')
@patch('src.Gui.data_utils.display_scatter_plot')
def test_load_csv_success(mock_display, mock_create_pages, mock_load_data, mock_askopen, dummy):
    data_utils.load_csv(dummy)
    assert dummy.file_path == 'fake_path.csv'
    assert dummy.data is not None
    mock_create_pages.assert_called_once_with(dummy)
    mock_display.assert_called_once_with(dummy)


@patch('src.Gui.data_utils.filedialog.asksaveasfilename')
def test_save_csv_with_data_and_deleted(mock_save_dialog, dummy, tmp_path):
    dummy.data = pd.DataFrame({'x':[1,2]})
    dummy.deleted_data = pd.DataFrame({'a':[1,2]})

    save_path = tmp_path / "save_path.csv"
    mock_save_dialog.return_value = str(save_path)

    data_utils.save_csv(dummy)

    assert dummy.file_path == str(save_path)
    assert save_path.exists()

    deleted_path = tmp_path / "save_path_deleted.csv"
    assert deleted_path.exists()



@patch('src.Gui.data_utils.messagebox.showwarning')
@patch('src.Gui.data_utils.load_data', return_value=None)
@patch('src.Gui.data_utils.filedialog.askopenfilename', return_value='fake_path.csv')
def test_load_csv_fail(mock_askopen, mock_load_data, mock_showwarning, dummy):
    data_utils.load_csv(dummy)
    mock_showwarning.assert_called_once_with("Chargement", "Échec du chargement des données")
    assert dummy.file_path == 'fake_path.csv'

    assert dummy.data is None



""" RAJOUTER SAVE_CSV FAILED"""