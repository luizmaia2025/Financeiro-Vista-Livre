import streamlit as st

# O `set_page_config` DEVE vir antes de qualquer outro código
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

import pandas as pd
import plotly.express as px

# URL pública da planilha no Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Cache para evitar recarregamento desnecessário
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)

    # Padronizar os nomes das colunas para evitar problemas de formatação
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()

    # Converter colunas de data corretamente
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], dayfirst=True, errors='coerce')
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], dayfirst=True, errors='coerce')

    # 🔹 Corrigir a conversão da coluna "Valor"
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    df_receber["Valor"] = df_receber["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"], errors='coerce')

    return df_pagar, df_receber

# Carregar os dados
df_pagar, df_receber = load_data()

st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# Sidebar - Filtros Interativos
st.sidebar.header("🔍 Filtros")

# Escolher entre "Data de Lançamento" ou "Data de Vencimento"
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

# Seleção do período
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por Categoria
categoria_opcoes = df_pagar["Categoria"].dropna().unique()
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default=categoria_opcoes)

# Filtro por Status
status_opcoes = df_pagar["Status (Pago/Em Aberto)"].dropna().unique()
status_selecionado = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default=status_opcoes)

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Categoria"].isin(categoria_selecionada)) &
    (df_pagar["Status (Pago/Em Aberto)"].isin(status_selecionado))
]

# ---- Exibir Tabela Filtrada ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# ---- Criar Gráficos ----
st.subheader("📈 Distribuição das Contas a Pagar")

# Gráfico de Valores por Categoria
fig_categoria = px.bar(df_filtrado, x="Categoria", y="Valor", color="Categoria", title="Total de Gastos por Categoria")
st.plotly_chart(fig_categoria, use_container_width=True)

# Gráfico de Valores por Status
fig_status = px.pie(df_filtrado, names="Status (Pago/Em Aberto)", values="Valor", title="Status das Contas a Pagar")
st.plotly_chart(fig_status, use_container_width=True)

# ---- Resumo Financeiro ----
st.sidebar.header("📊 Resumo")
total_gastos = df_filtrado["Valor"].sum()
media_gastos = df_filtrado["Valor"].mean()

st.sidebar.metric(label="💰 Total de Gastos", value=f"R$ {total_gastos:,.2f}")
st.sidebar.metric(label="📊 Média de Gastos", value=f"R$ {media_gastos:,.2f}")
