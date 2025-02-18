import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração da Página ----
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

# URL pública da planilha no Google Sheets
SHEET_ID = "1hxeG2XDXR3yWrKNCBgWdgUY0oX2z1jmD3iJitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

# Cache para evitar recarregamento desnecessário
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    return df_pagar

# Carregar os dados
df = load_data()

# Converter colunas de valores para numéricas
df["Valor"] = df["Valor"].replace('[\R$\s,]', '', regex=True).astype(float)

# Filtragem por intervalo de datas
data_inicial = st.sidebar.date_input("Data Inicial", value=pd.to_datetime("2025-01-01"))
data_final = st.sidebar.date_input("Data Final", value=pd.to_datetime("2025-01-31"))
df = df[(pd.to_datetime(df["Data de Vencimento"]) >= data_inicial) & (pd.to_datetime(df["Data de Vencimento"]) <= data_final)]

# Filtragem por Centro de Custo
centro_custo_filtro = st.sidebar.multiselect("Filtrar por Centro de Custo:", options=df["Centro de custo"].unique(), default=df["Centro de custo"].unique())
df_empresa = df[df["Centro de custo"].isin(centro_custo_filtro)]

# Resumo Financeiro (Apenas da Empresa, sem Cartão de Crédito)
custo_fixo_empresa = df_empresa[df_empresa["Categoria"] == "Fixo"]["Valor"].sum()
custo_variavel_empresa = df_empresa[df_empresa["Categoria"] == "Variável"]["Valor"].sum()
total_gastos_empresa = custo_fixo_empresa + custo_variavel_empresa

# Cartão de Crédito (Filtrado apenas por data)
df_cartao = df[df["Subtipo"] == "Cartão de Crédito"]
custo_fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
custo_variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()
total_cartao = custo_fixo_cartao + custo_variavel_cartao

# Layout - Exibição dos valores na interface
st.title("📊 Dashboard Financeiro - Vista Livre 2025")
st.subheader("📌 Resumo Financeiro")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Gastos Fixos (Empresa)", f"R$ {custo_fixo_empresa:,.2f}")
col2.metric("💸 Gastos Variáveis (Empresa)", f"R$ {custo_variavel_empresa:,.2f}")
col3.metric("🏦 Total de Gastos (Empresa)", f"R$ {total_gastos_empresa:,.2f}")

st.subheader("💳 Gastos no Cartão de Crédito")
st.metric("Total no Cartão de Crédito", f"R$ {total_cartao:,.2f}")
st.write(f"📌 **Fixos:** R$ {custo_fixo_cartao:,.2f} | 🎭 **Variáveis:** R$ {custo_variavel_cartao:,.2f}")

# Gráfico de Gastos por Centro de Custo
st.subheader("📈 Análises Financeiras")
fig_centro_custo = px.bar(df_empresa, x="Centro de custo", y="Valor", color="Categoria", title="Gastos por Centro de Custo", text_auto=True)
st.plotly_chart(fig_centro_custo, use_container_width=True)

# Exibição Final
st.write("---")
st.write("🔹 Os dados apresentados refletem os filtros aplicados.")
