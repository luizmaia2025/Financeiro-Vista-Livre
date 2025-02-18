import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração da Página ----
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

# ---- URL da Planilha Google Sheets ----
SHEET_ID = "1hxeG2XDXR3yWrKNCB9wdgUYx0Xz2lJimD3ii1tPboc"
SHEET_NAME = "contas_a_pagar"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# ---- Função para Carregar Dados ----
@st.cache_data
def load_data():
    try:
        df_pagar = pd.read_csv(SHEET_URL_PAGAR)
        return df_pagar
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = load_data()

# ---- Ajustando os tipos de dados ----
df["Data de Vencimento"] = pd.to_datetime(df["Data de Vencimento"], dayfirst=True)
df["Valor"] = df["Valor"].astype(float)

# ---- Filtros ----
st.sidebar.header("📌 Filtros")

# Filtro de intervalo de datas
data_inicial = st.sidebar.date_input("Data Inicial", df["Data de Vencimento"].min())
data_final = st.sidebar.date_input("Data Final", df["Data de Vencimento"].max())

# Filtro por centro de custo
centros_custo_unicos = df["Centro de Custo"].dropna().unique()
filtro_centro_custo = st.sidebar.multiselect("Filtrar por Centro de Custo:", centros_custo_unicos, default=centros_custo_unicos)

# Filtro por subtipo
subtipos_unicos = df["Subtipo"].dropna().unique()
filtro_subtipo = st.sidebar.multiselect("Filtrar por Subtipo:", subtipos_unicos, default=subtipos_unicos)

# ---- Aplicando os Filtros ----
df_filtrado = df[
    (df["Data de Vencimento"] >= pd.to_datetime(data_inicial)) &
    (df["Data de Vencimento"] <= pd.to_datetime(data_final)) &
    (df["Centro de Custo"].isin(filtro_centro_custo)) &
    (df["Subtipo"].isin(filtro_subtipo))
]

# ---- Resumo Financeiro da Empresa (Baseado no Centro de Custo) ----
df_empresa = df_filtrado.copy()

custo_fixo_empresa = df_empresa[df_empresa["Categoria"] == "Fixo"]["Valor"].sum()
custo_variavel_empresa = df_empresa[df_empresa["Categoria"] == "Variável"]["Valor"].sum()
total_gastos_empresa = custo_fixo_empresa + custo_variavel_empresa

# ---- Cartão de Crédito (Baseado Apenas na Data) ----
df_cartao = df[
    (df["Data de Vencimento"] >= pd.to_datetime(data_inicial)) &
    (df["Data de Vencimento"] <= pd.to_datetime(data_final)) &
    (df["Subtipo"] == "Cartão de crédito")
]

custo_fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
custo_variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()
total_cartao_credito = custo_fixo_cartao + custo_variavel_cartao

# ---- Exibição dos Dados ----
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# Resumo Financeiro
st.subheader("📌 Resumo Financeiro (Empresa)")
col1, col2, col3 = st.columns(3)
col1.metric("💰 Gastos Fixos (Empresa)", f"R$ {custo_fixo_empresa:,.2f}")
col2.metric("💸 Gastos Variáveis (Empresa)", f"R$ {custo_variavel_empresa:,.2f}")
col3.metric("📊 Total de Gastos (Empresa)", f"R$ {total_gastos_empresa:,.2f}")

# Cartão de Crédito
st.subheader("💳 Gastos no Cartão de Crédito")
st.metric("📌 Total no Cartão de Crédito", f"R$ {total_cartao_credito:,.2f}")
st.text(f"📌 Fixos: R$ {custo_fixo_cartao:,.2f}  |  📌 Variáveis: R$ {custo_variavel_cartao:,.2f}")

# ---- Gráficos ----
st.subheader("📈 Análises Financeiras")

# Gráfico de Gastos por Centro de Custo
fig_centro_custo = px.bar(df_empresa, x="Centro de Custo", y="Valor", color="Categoria", title="Gastos por Centro de Custo")
st.plotly_chart(fig_centro_custo, use_container_width=True)

# Gráfico de Distribuição Fixo vs Variável
fig_fixo_variavel = px.pie(df_empresa, names="Categoria", values="Valor", title="Distribuição de Gastos (Fixo vs Variável)")
st.plotly_chart(fig_fixo_variavel, use_container_width=True)

# ---- Tabela de Detalhes ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

