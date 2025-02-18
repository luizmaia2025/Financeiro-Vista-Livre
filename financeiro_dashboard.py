import streamlit as st
import pandas as pd
import plotly.express as px

# URL pública da planilha (versão CSV)
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    return df_pagar

# Carregar os dados
df_pagar = load_data()

# Renomeando colunas para garantir compatibilidade
colunas = [
    "Data lançamento", "Data de Vencimento", "Fornecedor", "Tipo", "Subtipo", "Centro de custo", "Produto",
    "Categoria", "Valor", "Objetivo", "Status (Pago/Em Aberto)", "Data de Pagamento", "Forma de Pagamento",
    "Observações", "Nota fiscal"
]
df_pagar.columns = colunas

# Convertendo colunas para os tipos corretos
df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "").str.replace(",", "").astype(float)
df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
df_pagar["Data de Pagamento"] = pd.to_datetime(df_pagar["Data de Pagamento"], dayfirst=True, errors='coerce')

# Sidebar de filtros
st.sidebar.header("🔍 Filtros")

data_filtro = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"], index=1)
categoria_filtro = st.sidebar.multiselect("Filtrar por Categoria:", df_pagar["Categoria"].unique())
status_filtro = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", df_pagar["Status (Pago/Em Aberto)"].dropna().unique())
forma_pagamento_filtro = st.sidebar.selectbox("Forma de Pagamento:", ["Todas"] + list(df_pagar["Forma de Pagamento"].dropna().unique()))
data_inicial = st.sidebar.date_input("Data Inicial", df_pagar["Data de Vencimento"].min())
data_final = st.sidebar.date_input("Data Final", df_pagar["Data de Vencimento"].max())

# Aplicar filtros
coluna_data = "Data de Vencimento" if data_filtro == "Data de Vencimento" else "Data lançamento"
df_filtrado = df_pagar[(df_pagar[coluna_data] >= pd.to_datetime(data_inicial)) & (df_pagar[coluna_data] <= pd.to_datetime(data_final))]
if categoria_filtro:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_filtro)]
if status_filtro:
    df_filtrado = df_filtrado[df_filtrado["Status (Pago/Em Aberto)"].isin(status_filtro)]
if forma_pagamento_filtro != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Forma de Pagamento"] == forma_pagamento_filtro]

# Indicadores financeiros
total_pagar = df_filtrado["Valor"].sum()
total_fixo = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
total_variavel = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()

# Exibição do Dashboard
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Contas a Pagar", f"R$ {total_pagar:,.2f}")
col2.metric("Total Fixo", f"R$ {total_fixo:,.2f}")
col3.metric("Total Variável", f"R$ {total_variavel:,.2f}")

# Tabela de dados filtrados
st.subheader("📄 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# Gráficos
st.subheader("📊 Distribuição das Contas a Pagar")
fig_categoria = px.bar(df_filtrado, x="Categoria", y="Valor", title="Contas a Pagar por Categoria")
st.plotly_chart(fig_categoria)

fig_centro_custo = px.pie(df_filtrado, names="Centro de custo", values="Valor", title="Distribuição por Centro de Custo")
st.plotly_chart(fig_centro_custo)
