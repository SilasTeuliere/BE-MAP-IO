import polars as pl
import numpy as np
from error_manager import log_error, init_error_log_file

def filter_data(df):
    """
    Filtre les données pour ne conserver que les lignes où la colonne 'ccn_flag' est égale à 0 et pollution flag = 0.
    
    param : dataframe contenant les données
    retour : dataframe filtré
    """
    init_error_log_file()  # Initialiser le fichier de log d'erreurs
    # Filtrer les données pour ne garder que celles où ccn_flag == 0 et pollution _flag == 0
    filtered_df = df.filter((df['ccn_flag'] == 0) & (df['pollution_flag'] == 0))

    #Recuperation des erreurs
    df_sorted = df.sort('datetime').to_pandas()

    in_error = False
    start_time = None
    end_time = None
    current_flag = None
    values = []

    for i, row in df_sorted.iterrows():
        pollution_flag = row['pollution_flag']
        ccn_flag = row['ccn_flag']
        datetime = row['datetime']
        value = row['ccn_conc']

        #Detecter les erreurs si pollution_flag != 0 ou ccn_flag != 0
        if pollution_flag != 0 or ccn_flag != 0:
            flag_code = pollution_flag if pollution_flag != 0 else ccn_flag
            if not in_error:
                in_error = True
                start_time = datetime
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
                start_time = None
                end_time = None
                current_flag = None
                values = []
    # Traiter le dernier enregistrement d'erreur s'il existe
    if in_error:
        end_time = df_sorted.iloc[-1]['datetime']
        moy_values = sum(values) / len(values)
        log_error(start_time, end_time, current_flag, moy_values)
    
    return filtered_df
'''
    #Recupérer les colonnes ou ccn_flag = 0
    erreur = df.filter((df['ccn_flag'] != 0) | (df['pollution_flag'] != 0))
    #recuperer les erreurs au bon format et les ecrire dans le fichier erreur
    for i in range(len(erreur)):
        start_time = erreur['datetime'][i]
        end_time = erreur['datetime'][i]
        if(erreur['pollution_flag'][i] != 0):
            error_code = erreur['pollution_flag'][i]
        else:
            error_code = erreur['ccn_flag'][i]
        error_value = erreur['ccn_conc'][i]
        log_error(start_time, end_time, error_code, error_value)
'''
    