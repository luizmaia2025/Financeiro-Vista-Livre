import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração da Página ----
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
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

# Seleção do período
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por Centro de Custo
centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

# 📌 **Filtragem dos dados para os valores gerais da empresa**
df_empresa = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado)) &
    (df_pagar["Subtipo"] != "Cartão de crédito")  # 🔹 Removendo cartão de crédito da análise geral
]

# 📌 **Filtragem específica para o Cartão de Crédito (sem centro de custo)**
df_cartao = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Subtipo"] == "Cartão de crédito")  # 🔹 Considerando apenas o cartão de crédito
]

# ---- Cálculo dos Valores ----
# 🏦 **Valores Gerais da Empresa (Sem Cartão de Crédito)**
total_gastos_empresa = df_empresa["Valor"].sum()
gastos_fixos_empresa = df_empresa[df_empresa["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis_empresa = df_empresa[df_empresa["Categoria"] == "Variável"]["Valor"].sum()

# 💳 **Valores Específicos do Cartão de Crédito**
total_cartao = df_cartao["Valor"].sum()
fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Layout Melhorado ----
st.markdown("### 📊 Resumo Financeiro (Empresa)")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏦 Gastos Fixos (Empresa)", value=f"R$ {gastos_fixos_empresa:,.2f}")
with col2:
    st.metric(label="📉 Gastos Variáveis (Empresa)", value=f"R$ {gastos_variaveis_empresa:,.2f}")
with col3:
    st.metric(label="💰 Total de Gastos (Empresa)", value=f"R$ {total_gastos_empresa:,.2f}")

st.markdown("---")

# Seção do Cartão de Crédito
st.subheader("💳 Gastos no Cartão de Crédito")
st.metric(label="💳 Total no Cartão de Crédito", value=f"R$ {total_cartao:,.2f}")
st.text(f"🔹 Fixos: R$ {fixo_cartao:,.2f}  |  🔸 Variáveis: R$ {variavel_cartao:,.2f}")

st.markdown("---")
