import streamlit as st

# O `set_page_config` DEVE ser o primeiro comando do script
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

    # Padronizar os nomes das colunas
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()

    # Converter colunas de data corretamente
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], dayfirst=True, errors='coerce')
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], dayfirst=True, errors='coerce')

    # Corrigir conversão de valores
    for df in [df_pagar, df_receber]:
        df["Valor"] = df["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df["Valor"] = pd.to_numeric(df["Valor"], errors='coerce')

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

# Filtro por Categoria (Adicionando opção "Todos")
categoria_opcoes = ["Todos"] + list(df_pagar["Categoria"].dropna().unique())
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")

# Filtro por Status (Adicionando opção "Todos")
status_opcoes = ["Todos"] + list(df_pagar["Status (Pago/Em Aberto)"].dropna().unique())
status_selecionado = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default="Todos")

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]

if "Todos" not in status_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Status (Pago/Em Aberto)"].isin(status_selecionado)]

# ---- Exibir Tabela Filtrada ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# ---- Indicadores Financeiros ----
st.sidebar.header("📊 Resumo Financeiro")

total_pagar = df_filtrado["Valor"].sum()
media_pagar = df_filtrado["Valor"].mean()
total_receber = df_receber["Valor"].sum()
fluxo_caixa = total_receber - total_pagar
pendente = df_pagar[df_pagar["Status (Pago/Em Aberto)"] != "Pago"]["Valor"].sum()

st.sidebar.metric(label="💰 Total a Pagar", value=f"R$ {total_pagar:,.2f}")
st.sidebar.metric(label="📊 Média de Pagamentos", value=f"R$ {media_pagar:,.2f}")
st.sidebar.metric(label="📈 Total a Receber", value=f"R$ {total_receber:,.2f}")
st.sidebar.metric(label="📊 Fluxo de Caixa", value=f"R$ {fluxo_caixa:,.2f}")
st.sidebar.metric(label="⚠️ Pendências em Aberto", value=f"R$ {pendente:,.2f}")

# ---- Gráficos ----
st.subheader("📈 Distribuição das Contas a Pagar")

# Gráfico de Valores por Categoria
fig_categoria = px.bar(df_filtrado, x="Categoria", y="Valor", color="Categoria", title="Total de Gastos por Categoria")
st.plotly_chart(fig_categoria, use_container_width=True)

# Gráfico de Valores por Status
fig_status = px.pie(df_filtrado, names="Status (Pago/Em Aberto)", values="Valor", title="Status das Contas a Pagar")
st.plotly_chart(fig_status, use_container_width=True)

# Gráfico Comparativo - Contas a Pagar x Contas a Receber
df_fluxo = pd.DataFrame({
    "Tipo": ["Contas a Pagar", "Contas a Receber"],
    "Valor": [total_pagar, total_receber]
})
fig_fluxo = px.bar(df_fluxo, x="Tipo", y="Valor", color="Tipo", title="Comparação de Pagamentos e Recebimentos")
st.plotly_chart(fig_fluxo, use_container_width=True)

