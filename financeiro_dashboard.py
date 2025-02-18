import pandas as pd
import streamlit as st
import plotly.express as px

# 🔹 Configuração da Página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# 🔹 URL CORRETA para carregar os dados no formato CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc/gviz/tq?tqx=out:csv"

# 🔹 Função para Carregar Dados
@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL)

    # 🔹 Ajustar nomes das colunas
    df.columns = df.columns.str.strip()

    # 🔹 Convertendo valores corretamente
    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # 🔹 Convertendo datas
    df["Data de Lançamento"] = pd.to_datetime(df["Data de Lançamento"], format="%d/%m/%Y", errors="coerce")
    df["Data de Vencimento"] = pd.to_datetime(df["Data de Vencimento"], format="%d/%m/%Y", errors="coerce")

    return df

# 🔹 Carregar os dados
try:
    df = load_data()
    st.success("✅ Dados carregados com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao carregar os dados: {e}")
    st.stop()

# 🔹 Exibir tabela para conferência
st.dataframe(df)
