import pandas as pd

from data_loader import load_data 

def main():
    file_path = r"data/Donnée Marion Dufresne/MAPIO-CCN_L1_20210205_20210208 (1).csv"
    df = load_data(file_path)
    if df is None or df.empty:
        print("Erreur lors du chargement des données.")
        return
    print(df.iloc[0])
    print("Fin du traitement des données.")



if __name__ == "__main__":
    main()