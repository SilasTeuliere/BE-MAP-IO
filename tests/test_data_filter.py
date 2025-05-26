import pandas as pd
import os
import sys

import tempfile
from pathlib import Path

# Ajout du chemin du module à tester
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_filter import filter_data
from src.error_manager import init_error_log_file, ERROR_LOG_FILE


# Test pour vérifier que toutes les données valides sont conservées

def test_filter_data_all_valid():
    df = pd.DataFrame({
        'datetime': pd.to_datetime(['2023-01-01 00:00', '2023-01-01 01:00']),
        'ccn_flag': [0, 0],
        'pollution_flag': [0, 0],
        'ccn_conc': [100, 200]
    })

    
# Appel de la fonction à tester
    result = filter_data(df)

    assert len(result) == 2
    assert all(result['ccn_flag'] == 0)
    assert all(result['pollution_flag'] == 0)

# Test pour vérifier le filtrage des données avec erreurs et la génération du log
def test_filter_data_with_errors(tmp_path):
    # Initialiser le log dans un fichier temporaire
    #error_log = tmp_path / "error_log.txt"
    from src import error_manager
    error_manager.init_error_log_file()
    error_log = Path(error_manager.ERROR_LOG_FILE)

    # Fichier de dico pour la description
    dico_path = os.path.join(os.path.dirname(__file__), "..", "data", "dico_error.json")
    with open(dico_path, "w", encoding="utf-8") as f:
        import json
        json.dump({"1": "Erreur pollution", "2": "Erreur CCN"}, f)

    df = pd.DataFrame({
        'datetime': pd.to_datetime([
            '2023-01-01 00:00',
            '2023-01-01 01:00',
            '2023-01-01 02:00',
            '2023-01-01 03:00',
        ]),
        'ccn_flag': [0, 1, 1, 0],
        'pollution_flag': [0, 0, 1, 0],
        'ccn_conc': [100, 150, 200, 300]
    })

    result = filter_data(df)

    assert len(result) == 2
    assert list(result['ccn_conc']) == [100, 300]

    # Vérif log
    assert error_log.exists()
    content = error_log.read_text()
    assert "Erreur pollution" in content or "Erreur CCN" in content


# Test pour vérifier le comportement lorsque toutes les données sont invalides
def test_filter_data_all_invalid(tmp_path):
    #error_log = tmp_path / "log_all_invalid.txt"
    from src import error_manager
    error_manager.init_error_log_file()
    error_log = Path(error_manager.ERROR_LOG_FILE)

    df = pd.DataFrame({
        'datetime': pd.date_range("2023-01-01", periods=3, freq='H'),
        'ccn_flag': [1, 1, 2],
        'pollution_flag': [0, 1, 0],
        'ccn_conc': [100, 150, 180]
    })

    result = filter_data(df)

    assert result.empty
    assert error_log.exists()

# Test pour vérifier que les erreurs au début des données sont correctement loguées

def test_error_starts_first_row(tmp_path):
    from src import error_manager
    error_manager.init_error_log_file()
    error_log = Path(error_manager.ERROR_LOG_FILE)

    df = pd.DataFrame({
        'datetime': pd.to_datetime(['2023-01-01 00:00', '2023-01-01 01:00', '2023-01-01 02:00']),
        'ccn_flag': [1, 0, 0],
        'pollution_flag': [0, 0, 0],
        'ccn_conc': [50, 100, 150]
    })

    result = filter_data(df)

    # Le filtrage doit garder que les lignes valides (flags = 0)
    assert len(result) == 2
    assert all(result['ccn_flag'] == 0)

    # Le log d’erreur doit exister et contenir les infos sur la première erreur
    assert error_log.exists()
    content = error_log.read_text()
    assert "1" in content  # flag d’erreur dans le log
    assert "2023-01-01 00:00" in content  # début de l’erreur

# Test pour vérifier que plusieurs segments d’erreurs sont correctement logués
def test_multiple_error_segments(tmp_path):
    from src import error_manager
    error_manager.init_error_log_file()
    error_log = Path(error_manager.ERROR_LOG_FILE)

    df = pd.DataFrame({
        'datetime': pd.to_datetime([
            '2023-01-01 00:00',
            '2023-01-01 01:00',
            '2023-01-01 02:00',
            '2023-01-01 03:00',
            '2023-01-01 04:00',
        ]),
        'ccn_flag': [0, 1, 1, 0, 2],
        'pollution_flag': [0, 0, 0, 0, 0],
        'ccn_conc': [10, 20, 30, 40, 50]
    })

    result = filter_data(df)

    # On garde que les lignes sans erreur (flag=0)
    assert len(result) == 2
    assert list(result['ccn_conc']) == [10, 40]

    # Le fichier log doit contenir au moins 2 segments d’erreurs
    assert error_log.exists()
    content = error_log.read_text()
    assert content.count("1") >= 1
    assert content.count("2") >= 1
