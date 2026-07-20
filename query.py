import mysql.connector
import streamlit as st

# Conexão com o banco de dados
conn = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    passwd="Junior15@",
    db="meudb"
)

# Função única e protegida com Cache para não derrubar o MySQL
@st.cache_data
def view_all_data():
    c = conn.cursor()
    c.execute('select * from insurance')
    data = c.fetchall()
    c.close() # Fecha o cursor para liberar memória do banco
    return data
