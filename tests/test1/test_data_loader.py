import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import load_data

def test_load_data_valid(tmp_path):
    # Création d’un petit CSV temporaire pour tester
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({
        'datetime': ['2023-01-01', '2023-01-02'],
        'pollution_flag': [0, 0],
        'ccn_flag': [0, 0],
        'ccn_sursaturation': [0.3, 0.4],
        'ccn_conc': [120, 130]
    })
    df.to_csv(file_path, index=False)

    # Chargement via load_data
    result = load_data(file_path)

    # Vérifications
    assert result is not None #données bien charées
    assert len(result) == 2
    assert 'ccn_conc' in result.columns

def test_load_data_missing_columns(tmp_path):
    file_path = tmp_path / "test_incomplet.csv"
    df = pd.DataFrame({
        'datetime': ['2023-01-01'],
        'pollution_flag': [0],
        'ccn_flag': [0],
        # il manque les deux autres colonnes
    })
    df.to_csv(file_path, index=False)

    result = load_data(file_path)
    assert result is None

#a ajouter Test pour les données mal formatées & Test pour un fichier vide 
