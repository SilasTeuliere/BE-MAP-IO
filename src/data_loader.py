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
        print ( df.head())
        dffiltrer = filter_data(df)
        print (dffiltrer.head())
    except Exception as e:
        print(f"erreur chargement des donnés: {e}")
        return None
    return dffiltrer  