import streamlit as st

# O `set_page_config` DEVE vir antes de qualquer outro código
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

import pandas as pd
import plotly.express as px

# URL pública da planilha no Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

# Cache para evitar recarregamento desnecessário
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)

    # Padronizar os nomes das colunas para evitar problemas de formatação
    df_pagar.columns = df_pagar.columns.str.strip()

    # 🔹 Padronizando a coluna "Categoria" para evitar erro de identificação
    df_pagar["Categoria"] = df_pagar["Categoria"].astype(str).str.strip().str.lower()

    # Converter colunas de data corretamente
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')

    # 🔹 Corrigir a conversão da coluna "Valor"
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    return df_pagar

# Carregar os dados
df_pagar = load_data()

# 🔹 Padronizando a coluna Categoria
df_pagar["Categoria"] = df_pagar["Categoria"].replace({
    "fixo": "Fixo", 
    "variável": "Variável"
})

# ---- Filtros Avançados ----
with st.sidebar:
    st.header("🔍 Filtros")

    # Filtro de Data
    st.subheader("📅 Filtrar por Período")
    data_tipo = st.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
    data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
    data_inicio = st.date_input("Data Inicial", df_pagar[data_coluna].min())
    data_fim = st.date_input("Data Final", df_pagar[data_coluna].max())

    # Criar opções para seleção múltipla e adicionar "Todos"
    def adicionar_todos(lista):
        return ["Todos"] + list(lista)

    # Filtros Avançados
    categoria_opcoes = adicionar_todos(df_pagar["Categoria"].dropna().unique())
    centro_custo_opcoes = adicionar_todos(df_pagar["Centro de custo"].dropna().unique())

    # Seleção de Filtros
    st.subheader("📂 Categorias")
    categoria_selecionada = st.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")

    st.subheader("🏢 Centro de Custo")
    centro_custo_selecionado = st.multiselect("Filtrar por Centro de Custo:", centro_custo_opcoes, default="Todos")

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]
if "Todos" not in centro_custo_selecionado:
    df_filtrado = df_filtrado[df_fil
