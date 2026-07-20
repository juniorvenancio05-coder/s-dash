import pandas as pd
import streamlit as st
import os


def view_all_data():
    # Caminho do arquivo exportado
    arquivo_csv = "insurance.csv"

    # Verifica se o arquivo existe para não quebrar o app
    if os.path.exists(arquivo_csv):
        # Lê o CSV e converte em uma lista de tuplas idêntica ao fetchall() do MySQL
        df = pd.read_csv(arquivo_csv)
        return df.to_records(index=False).tolist()
    else:
        # Retorna uma lista vazia caso o arquivo não seja encontrado
        return []
