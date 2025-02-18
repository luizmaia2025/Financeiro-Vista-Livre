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

# Sidebar - Filtros Avançados
st.sidebar.header("🔍 Filtros")

# Escolher entre "Data de Lançamento" ou "Data de Vencimento"
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

# Seleção do período
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Criar opções para seleção múltipla e adicionar "Todos"
def adicionar_todos(lista):
    return ["Todos"] + list(lista)

# Filtros Avançados
categoria_opcoes = adicionar_todos(df_pagar["Categoria"].dropna().unique())
centro_custo_opcoes = adicionar_todos(df_pagar["Centro de custo"].dropna().unique())
tipo_opcoes = adicionar_todos(df_pagar["Tipo"].dropna().unique())
subtipo_opcoes = adicionar_todos(df_pagar["Subtipo"].dropna().unique())
status_opcoes = adicionar_todos(df_pagar["Status (Pago/Em Aberto)"].dropna().unique())

# Seleção de Filtros
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")
centro_custo_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_custo_opcoes, default="Todos")
tipo_selecionado = st.sidebar.multiselect("Filtrar por Tipo:", tipo_opcoes, default="Todos")
subtipo_selecionado = st.sidebar.multiselect("Filtrar por Subtipo:", subtipo_opcoes, default="Todos")
status_selecionado = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default="Todos")

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]
if "Todos" not in centro_custo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Centro de custo"].isin(centro_custo_selecionado)]
if "Todos" not in tipo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipo_selecionado)]
if "Todos" not in subtipo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Subtipo"].isin(subtipo_selecionado)]
if "Todos" not in status_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Status (Pago/Em Aberto)"].isin(status_selecionado)]

# ---- Exibir Tabela Filtrada ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# ---- Indicadores Financeiros ----
st.sidebar.header("📊 Resumo Financeiro")

total_gastos = df_filtrado["Valor"].sum()
media_gastos = df_filtrado["Valor"].mean()

fixo = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
variavel = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()

st.sidebar.metric(label="💰 Total de Gastos", value=f"R$ {total_gastos:,.2f}")
st.sidebar.metric(label="📊 Média de Gastos", value=f"R$ {media_gastos:,.2f}")
st.sidebar.metric(label="🏦 Gastos Fixos", value=f"R$ {fixo:,.2f}")
st.sidebar.metric(label="📉 Gastos Variáveis", value=f"R$ {variavel:,.2f}")

# ---- Criar Gráficos ----
st.subheader("📈 Análises Financeiras")

# Gráfico de Gastos Fixos x Variáveis
fig_fixo_variavel = px.pie(
    names=["Fixos", "Variáveis"], 
    values=[fixo, variavel], 
    title="Distribuição: Fixos x Variáveis"
)
st.plotly_chart(fig_fixo_variavel, use_container_width=True)

# Gráfico de Gastos por Centro de Custo
fig_centro_custo = px.bar(
    df_filtrado, 
    x="Centro de custo", 
    y="Valor", 
    color="Centro de custo", 
    title="Gastos por Centro de Custo"
)
st.plotly_chart(fig_centro_custo, use_container_width=True)
