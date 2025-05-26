import pandas as pd
from data_filter import filter_data

def load_data(file_path) :
    """
    Charge un fichier csv en récupérant uniquement les colonnes :
    - datetime
    -pollution_flag
    -ccn_flag
    -ccn_sursaturation
    -cc_conc

    param : chemin du fichier de données CSV
    retour : dataframe contenant les données chargées

    """
    try:
        data = pd.read_csv(file_path)
        columns = {'datetime', 'pollution_flag', 'ccn_flag', 'ccn_sursaturation', 'ccn_conc'}
        missing_columns = columns - set(data.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in the CSV file: {missing_columns}")
        df = data[list(columns)]
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce') #rajout test
        df_filtered = filter_data(df)
        return df_filtered
    except Exception as e:
        import traceback
        from tkinter import messagebox
        print(f"erreur chargement des donnés: {e}")
        traceback.print_exc()
        messagebox.showerror("Erreur", f"Erreur lors du chargement des données :\n{e}")
        return None
    # except Exception as e:
    #     print(f"erreur chargement des donnés: {e}")
    #     return None