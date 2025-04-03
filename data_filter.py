def filter_data(df)
    """
    Filtre les données pour ne conserver que les lignes où la colonne 'ccn_flag' est égale à 0 et pollution flag = 0.
    
    param : dataframe contenant les données
    retour : dataframe filtré
    """
    # Filtrer les données pour ne garder que celles où ccn_flag == 0 et pollution _flag == 0
    filtered_df = df[(df['ccn_flag'] == 0) & (df['pollution_flag'] == 0)]

    #Recuperation des erreurs
    errors = []
    #Recupérer les colonnes ou ccn_flag = 0
    erreur =  df[(df['ccn_flag'] != 0) & (df['pollution_flag'] != 0)]
    #2crire  les colonnes dans le fichier erreur.csv

    
    return filtered_df