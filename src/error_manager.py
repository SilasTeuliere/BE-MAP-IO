from datetime import datetime
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICO_PATH = os.path.join(BASE_DIR, "data", "dico_error.json")
ERROR_LOG_FILE = None

def init_error_log_file():
    """
    Initialise le fichier de log d'erreurs en ajoutant un en-tête.
    """
    global ERROR_LOG_FILE
    date_str = datetime.now().strftime("%Y-%m-%d")
    ERROR_LOG_FILE = f"CCN_ERR_LOG_V1_{date_str}.txt"
    en_tete = [
        "#acquisition error/standby/quality issue events\n",
        "Start Time;End Time;Error Description;Error Value\n",
        f"# --- {datetime.now().year} --- #\n"
    ]
    with open(ERROR_LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(en_tete)

def log_error(start_time, end_time, error_code, error_value):
    """
    Enregistre une erreur dans le fichier de log d'erreurs.
    param start_time: Heure de début de l'erreur
    param end_time: Heure de fin de l'erreur
    param error_code: Code de l'erreur
    param error_value: Valeur associée à l'erreur
    """

    global ERROR_LOG_FILE
    if ERROR_LOG_FILE is None:
        raise RuntimeError("Le fichier de log d'erreurs n'a pas été initialisé.")
    
    with open(DICO_PATH, "r", encoding="utf-8") as f:
        dico_error = json.load(f)

    description = dico_error.get(str(error_code), "Erreur inconnue")

    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{start_time};{end_time};{description};{error_value}\n")

def log_error_batch(error_list):
    """
    Enregistre une liste d'erreurs dans le fichier de log d'erreurs.
    param error_list: Liste d'erreurs à enregistrer
    """
    global ERROR_LOG_FILE
    if ERROR_LOG_FILE is None:
        raise RuntimeError("Le fichier de log d'erreurs n'a pas été initialisé.")
    
    with open(DICO_PATH, "r", encoding="utf-8") as f:
        dico_error = json.load(f)

    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        for start_time, end_time, error_code, error_value in error_list:
            description = dico_error.get(str(error_code), "Erreur inconnue")
            f.write(f"{start_time};{end_time};{description};{error_value}\n")