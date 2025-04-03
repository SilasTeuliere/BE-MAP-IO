import pandas as pd

from data_loader import load_data 

def main():
    file_path = r"Donnée Encadrant/MAPIO-SMPS_L1_20240210_20240215.csv"
    df = load_data(file_path)
    if df is None or df.empty:
        print("Erreur lors du chargement des données.")
        return
    print(df.iloc[0])
    file_path = r"Donnée Encadrant/MAPIO-CCN_L1_20210205_20210208 (1).csv"
    df = load_data(file_path)
    if df is None or df.empty:
        print("Erreur lors du chargement des données.")
        return
    print(df.iloc[0])



if __name__ == "__main__":
    main()