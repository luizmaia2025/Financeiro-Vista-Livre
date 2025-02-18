import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

# URL pública da planilha no Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

# Cache para evitar recarregamento desnecessário
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_pagar.columns = df_pagar.columns.str.strip()
    
    # Conversão de colunas de data
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
    
    # Conversão da coluna de valores
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False)
    df_pagar["Valor"] = df_pagar["Valor"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')
    
    return df_pagar

# Carregar os dados
df_pagar = load_data()

st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# ---- Sidebar - Filtros ----
st.sidebar.header("🎛️ Filtros")

# Escolher entre "Data de Lançamento" ou "Data de Vencimento"
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"], index=1)
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

# Seleção do Período
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por Categoria
categoria_opcoes = ["Todos"] + list(df_pagar["Categoria"].dropna().unique())
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")

# Filtro por Centro de Custo
centro_opcoes = ["Todos"] + list(df_pagar["Centro de custo"].dropna().unique())
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default="Todos")

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]

if "Todos" not in centro_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Centro de custo"].isin(centro_selecionado)]

# ---- Resumo Financeiro ----
st.markdown("---")
col1, col2, col3 = st.columns(3)

custo_fixo = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
custo_variavel = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()
total_gastos = df_filtrado["Valor"].sum()

col1.metric("🏛️ Gastos Fixos", f"R$ {custo_fixo:,.2f}")
col2.metric("🎭 Gastos Variáveis", f"R$ {custo_variavel:,.2f}")
col3.metric("💰 Total de Gastos", f"R$ {total_gastos:,.2f}")

# ---- Análise do Cartão de Crédito ----
cartao_filtro = df_filtrado[df_filtrado["Tipo"] == "Cartão de crédito"]
gasto_cartao = cartao_filtro["Valor"].sum()
gasto_cartao_fixo = cartao_filtro[cartao_filtro["Categoria"] == "Fixo"]["Valor"].sum()
gasto_cartao_variavel = cartao_filtro[cartao_filtro["Categoria"] == "Variável"]["Valor"].sum()

st.metric("💳 Gastos no Cartão de Crédito", f"R$ {gasto_cartao:,.2f}")
st.caption(f"📌 **Detalhamento:**\n 🏛️ Fixos: R$ {gasto_cartao_fixo:,.2f} | 🎭 *Variáveis* : R$ {gasto_cartao_variavel:,.2f}")

# ---- Gráficos ----
st.subheader("📊 Análises Financeiras")

col_graf1, col_graf2 = st.columns(2)

# Gráfico de Gastos por Centro de Custo
fig_centro_custo = px.bar(df_filtrado, x="Centro de custo", y="Valor", color="Centro de custo", title="Gastos por Centro de Custo")
col_graf1.plotly_chart(fig_centro_custo, use_container_width=True)

# Gráfico de Gastos por Categoria
fig_categoria = px.pie(df_filtrado, names="Categoria", values="Valor", title="Distribuição dos Gastos (Fixo vs Variável)")
col_graf2.plotly_chart(fig_categoria, use_container_width=True)

# Exibir Tabela Filtrada
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)
