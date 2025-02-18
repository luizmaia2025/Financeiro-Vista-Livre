import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha do Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Carregar os dados das planilhas
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)

    # Exibir os nomes das colunas carregadas para depuração
    st.write("🔍 Colunas em Contas a Pagar:", df_pagar.columns.tolist())
    st.write("🔍 Colunas em Contas a Receber:", df_receber.columns.tolist())

    return df_pagar, df_receber

# Criar o dashboard
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

df_pagar, df_receber = load_data()
