import os
import json
from datetime import datetime

from src import error_manager


def test_init_error_log_file_creates_file(tmp_path):
    # Rediriger le fichier dans un dossier temporaire
    error_manager.ERROR_LOG_FILE = tmp_path / "log_test.txt"
    with open(error_manager.ERROR_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")  # Fichier vide pour éviter RuntimeError

    error_manager.init_error_log_file()
    assert os.path.exists(error_manager.ERROR_LOG_FILE)

    with open(error_manager.ERROR_LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Start Time;End Time;Error Description;Error Value" in content


def test_log_error_writes_line(tmp_path):
    # Préparer le log et le dico
    error_manager.ERROR_LOG_FILE = tmp_path / "log_error.txt"

    dico_path = tmp_path / "dico_error.json"
    dico_data = {"1": "Flag pollution détecté"}
    dico_path.write_text(json.dumps(dico_data), encoding="utf-8")
    error_manager.DICO_PATH = str(dico_path)

    # Initialiser le fichier
    with open(error_manager.ERROR_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("Start Time;End Time;Error Description;Error Value\n")

    error_manager.log_error("2025-01-01 00:00", "2025-01-01 01:00", 1, 123.45)

    content = error_manager.ERROR_LOG_FILE.read_text(encoding="utf-8")
    assert "Flag pollution détecté" in content
    assert "123.45" in content


def test_log_error_batch(tmp_path):
    # Préparer fichier et dico
    error_manager.ERROR_LOG_FILE = tmp_path / "log_batch.txt"

    dico_path = tmp_path / "dico_error.json"
    dico_data = {"2": "Flag CCN incorrect"}
    dico_path.write_text(json.dumps(dico_data), encoding="utf-8")
    error_manager.DICO_PATH = str(dico_path)

    # Init du fichier
    with open(error_manager.ERROR_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("Start Time;End Time;Error Description;Error Value\n")

    error_list = [
        ("2025-01-02 00:00", "2025-01-02 01:00", 2, 456.78),
        ("2025-01-03 00:00", "2025-01-03 01:00", 2, 789.01),
    ]

    error_manager.log_error_batch(error_list)

    content = error_manager.ERROR_LOG_FILE.read_text(encoding="utf-8")
    assert "Flag CCN incorrect" in content
    assert "456.78" in content
    assert "789.01" in content
