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

    # 🔹 Padronizando a coluna "Categoria" para evitar erro de identificação
    df_pagar["Categoria"] = df_pagar["Categoria"].astype(str).str.strip().str.lower()

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

# ---- Layout Principal ----
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# 🔹 Indicadores principais no topo
fixo = df_pagar[df_pagar["Categoria"] == "Fixo"]["Valor"].sum()
variavel = df_pagar[df_pagar["Categoria"] == "Variável"]["Valor"].sum()

col1, col2 = st.columns(2)
col1.metric(label="🏦 Gastos Fixos", value=f"R$ {fixo:,.2f}")
col2.metric(label="📉 Gastos Variáveis", value=f"R$ {variavel:,.2f}")

# ---- Filtros Avançados ----
with st.expander("🔍 Filtros Avançados", expanded=True):
    col_filtros1, col_filtros2, col_filtros3 = st.columns(3)

    # Filtro de Data
    with col_filtros1:
        st.subheader("📅 Filtrar por Período")
        data_tipo = st.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
        data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
        data_inicio = st.date_input("Data Inicial", df_pagar[data_coluna].min())
        data_fim = st.date_input("Data Final", df_pagar[data_coluna].max())

    # Criar opções para seleção múltipla e adicionar "Todos"
    def adicionar_todos(lista):
        return ["Todos"] + list(lista)

    # 🔹 Padronizando a coluna Categoria
    df_pagar["Categoria"] = df_pagar["Categoria"].replace({
        "fixo": "Fixo", 
        "variável": "Variável"
    })

    # Filtros Avançados
    categoria_opcoes = adicionar_todos(df_pagar["Categoria"].dropna().unique())
    centro_custo_opcoes = adicionar_todos(df_pagar["Centro de custo"].dropna().unique())

    # Seleção de Filtros
    with col_filtros2:
        st.subheader("📂 Categorias")
        categoria_selecionada = st.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")

    with col_filtros3:
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
    df_filtrado = df_filtrado[df_filtrado["Centro de custo"].isin(centro_custo_selecionado)]

# ---- Exibir Tabela Filtrada ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# ---- Gráficos ----
st.subheader("📊 Análises Financeiras")

col_graf1, col_graf2 = st.columns(2)

# 🔹 Gráfico de Gastos por Centro de Custo
fig_centro_custo = px.bar(df_filtrado, 
                          x="Centro de custo", 
                          y="Valor", 
                          color="Centro de custo", 
                          title="Gastos por Centro de Custo",
                          text_auto=True)
col_graf1.plotly_chart(fig_centro_custo, use_container_width=True)

# 🔹 Gráfico de Distribuição de Gastos Fixos vs Variáveis
fig_pizza = px.pie(df_filtrado, 
                   names="Categoria", 
                   values="Valor", 
                   title="Distribuição de Gastos Fixos vs Variáveis",
                   hole=0.4)
col_graf2.plotly_chart(fig_pizza, use_container_width=True)

# ---- Resumo Financeiro ----
st.sidebar.header("📊 Resumo Financeiro")

total_gastos = df_filtrado["Valor"].sum()
media_gastos = df_filtrado["Valor"].mean()

st.sidebar.metric(label="💰 Total de Gastos", value=f"R$ {total_gastos:,.2f}")
st.sidebar.metric(label="📊 Média de Gastos", value=f"R$ {media_gastos:,.2f}")
st.sidebar.metric(label="🏦 Gastos Fixos", value=f"R$ {fixo:,.2f}")
st.sidebar.metric(label="📉 Gastos Variáveis", value=f"R$ {variavel:,.2f}")
