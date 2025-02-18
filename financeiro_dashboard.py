import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração do Tema ----
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

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

    # Corrigir formatação da coluna "Valor"
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    return df_pagar

# Carregar os dados
df_pagar = load_data()

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

# Filtro por Subtipo
subtipo_opcoes = df_pagar["Subtipo"].dropna().unique()
subtipo_selecionado = st.sidebar.multiselect("Filtrar por Subtipo:", subtipo_opcoes, default=subtipo_opcoes)

# Filtro por Centro de Custo
centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Categoria"].isin(categoria_selecionada)) &
    (df_pagar["Subtipo"].isin(subtipo_selecionado)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Cálculo dos Valores ----
total_gastos = df_filtrado["Valor"].sum()
gastos_fixos = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()

# **Cartão de Crédito - Considerando Apenas o Período Selecionado**
df_cartao = df_filtrado[df_filtrado["Subtipo"] == "Cartão de crédito"]
total_cartao = df_cartao["Valor"].sum()
fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Layout Melhorado ----
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏦 Gastos Fixos", value=f"R$ {gastos_fixos:,.2f}")
with col2:
    st.metric(label="📉 Gastos Variáveis", value=f"R$ {gastos_variaveis:,.2f}")
with col3:
    st.metric(label="💰 Total de Gastos", value=f"R$ {total_gastos:,.2f}")

st.markdown("---")

# Seção do Cartão de Crédito
st.subheader("💳 Gastos no Cartão de Crédito")
st.metric(label="💳 Total no Cartão de Crédito", value=f"R$ {total_cartao:,.2f}")
st.text(f"🔹 Fixos: R$ {fixo_cartao:,.2f}  |  🔸 Variáveis: R$ {variavel_cartao:,.2f}")

st.markdown("---")

# ---- Análises Financeiras ----
st.subheader("📈 Análises Financeiras")

# Gráfico de Gastos por Centro de Custo
fig_centro_custo = px.bar(df_filtrado, x="Centro de custo", y="Valor", color="Centro de custo",
                          title="Gastos por Centro de Custo", text_auto=True, height=400)
st.plotly_chart(fig_centro_custo, use_container_width=True)

# Tabela ao lado do gráfico
st.subheader("📋 Resumo por Centro de Custo")
df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
st.dataframe(df_resumo_centro, hide_index=True, use_container_width=True)

st.markdown("---")

# Gráfico de Distribuição Fixo x Variável
fig_fixo_variavel = px.pie(df_filtrado, names="Categoria", values="Valor", title="Distribuição dos Gastos (Fixo vs Variável)")
st.plotly_chart(fig_fixo_variavel, use_container_width=True)

st.markdown("---")

# Tabela Completa dos Dados Filtrados
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

