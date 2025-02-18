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

    # Converter colunas de data corretamente
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')

    # Corrigir a conversão da coluna "Valor"
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    return df_pagar

# Carregar os dados
df_pagar = load_data()

# ---- Filtros Avançados ----
st.sidebar.header("🔍 Filtros")

data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

# Definir intervalo de datas
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Criar opções para seleção múltipla e adicionar "Todos"
def adicionar_todos(lista):
    return ["Todos"] + list(lista)

# Filtros adicionais
categoria_opcoes = adicionar_todos(df_pagar["Categoria"].dropna().unique())
centro_custo_opcoes = adicionar_todos(df_pagar["Centro de custo"].dropna().unique())

# Aplicar filtros adicionais
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")
centro_custo_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_custo_opcoes, default="Todos")

df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]
if "Todos" not in centro_custo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Centro de custo"].isin(centro_custo_selecionado)]

# ---- Calcular valores dentro do período filtrado ----
fixo = df_filtrado[df_filtrado["Categoria"].str.strip() == "Fixo"]["Valor"].sum()
variavel = df_filtrado[(df_filtrado["Categoria"].str.strip() == "Variável") & (df_filtrado["Centro de custo"] != "Comissão de Vendas")]["Valor"].sum()
total_gastos = fixo + variavel

# 🔹 Cartão de Crédito Correto
df_cartao = df_filtrado[df_filtrado["Tipo"].str.contains("Cartão de Crédito", na=False)]
cartao_credito = df_cartao["Valor"].sum()
cartao_fixo = df_cartao[df_cartao["Categoria"].str.strip() == "Fixo"]["Valor"].sum()
cartao_variavel = df_cartao[df_cartao["Categoria"].str.strip() == "Variável"]["Valor"].sum()

# ---- Layout Melhorado ----
st.markdown("<h1 style='text-align: center;'>📊 Dashboard Financeiro - Vista Livre 2025</h1>", unsafe_allow_html=True)

# 🔹 Indicadores principais organizados conforme a nova estrutura
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric(label="🏦 Gastos Fixos", value=f"R$ {fixo:,.2f}")
col2.metric(label="📉 Gastos Variáveis", value=f"R$ {variavel:,.2f}")
col3.metric(label="💰 Total de Gastos", value=f"R$ {total_gastos:,.2f}")

st.markdown("---")
col_cartao1, col_cartao2 = st.columns(2)
col_cartao1.metric(label="💳 Gastos no Cartão de Crédito", value=f"R$ {cartao_credito:,.2f}")
col_cartao2.markdown(f"📌 **Detalhamento:**<br>🏦 Fixos: R$ {cartao_fixo:,.2f} | 📉 Variáveis: R$ {cartao_variavel:,.2f}", unsafe_allow_html=True)

st.markdown("---")

# ---- Filtros Avançados Melhorados ----
with st.expander("🔍 Filtros Avançados", expanded=True):
    col_filtros1, col_filtros2, col_filtros3 = st.columns(3)

    with col_filtros1:
        st.subheader("📅 Período")
        st.date_input("Data Inicial", df_pagar[data_coluna].min(), key="data_inicio")
        st.date_input("Data Final", df_pagar[data_coluna].max(), key="data_fim")

    with col_filtros2:
        st.subheader("📂 Categorias")
        st.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")

    with col_filtros3:
        st.subheader("🏢 Centro de Custo")
        st.multiselect("Filtrar por Centro de Custo:", centro_custo_opcoes, default="Todos")

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
