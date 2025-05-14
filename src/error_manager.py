from datetime import datetime
import json

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
    global ERROR_LOG_FILE
    if ERROR_LOG_FILE is None:
        raise RuntimeError("Le fichier de log d'erreurs n'a pas été initialisé.")
    
    with open("data/dico_error.json", "r", encoding="utf-8") as f:
        dico_error = json.load(f)

    description = dico_error.get(str(error_code), "Erreur inconnue")

    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{start_time};{end_time};{description};{error_value}\n")
