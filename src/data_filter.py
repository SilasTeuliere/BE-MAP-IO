import pandas as pd
import numpy as np
from error_manager import log_error, init_error_log_file

def filter_data(df):
    """
    Filtre les données pour ne conserver que les lignes où la colonne 'ccn_flag' est égale à 0 et pollution flag = 0.
    
    param : dataframe contenant les données
    retour : dataframe filtré
    """

    print(" Chargement du fichier CSV...")

    init_error_log_file()
    filtered_df = df[(df['ccn_flag'] == 0) & (df['pollution_flag'] == 0)]

    df_sorted = df.sort_values('datetime')

    print(f"Chargement terminé ")

    in_error = False
    start_time = None
    end_time = None
    current_flag = None
    values = []
    print(" Filtrage des données...")
    for i, row in df_sorted.iterrows():
        pollution_flag = row['pollution_flag']
        ccn_flag = row['ccn_flag']
        datetime_val = row['datetime']
        value = row['ccn_conc']

        if pollution_flag != 0 or ccn_flag != 0:
            flag_code = pollution_flag if pollution_flag != 0 else ccn_flag
            if not in_error:
                in_error = True
                start_time = datetime_val
                current_flag = flag_code
                values = [value]
            else:
                values.append(value)
        else:
            if in_error:
                end_time = df_sorted.iloc[i - 1]['datetime']
                moy_values = sum(values) / len(values)
                log_error(start_time, end_time, current_flag, moy_values)
                in_error = False
                values = []

    if in_error:
        end_time = df_sorted.iloc[-1]['datetime']
        moy_values = sum(values) / len(values)
        log_error(start_time, end_time, current_flag, moy_values)
    print(f" Filtrage terminé")

    return filtered_df