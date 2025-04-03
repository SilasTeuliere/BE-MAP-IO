def load_data(fil_path) :
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

    columns = ['datetime', 'pollution_flag', 'ccn_flag', 'ccn_sursaturation', 'cc_conc']
    df = pd.read_csv(fil_path, usecols=columns)
    df.head()
    dffiltrer = filter_data(df)
    dffiltrer.head()
    return dffiltrer  