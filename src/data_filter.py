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
    return filtered_df