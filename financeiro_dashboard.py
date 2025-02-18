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

# Filtro por Centro de Custo
centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Cálculo dos Valores ----
gastos_fixos = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()
total_gastos = df_filtrado["Valor"].sum()

# **Cartão de Crédito - Considerando Apenas o Período Selecionado**
df_cartao = df_filtrado[df_filtrado["Subtipo"] == "Cartão de crédito"]
total_cartao = df_cartao["Valor"].sum()
fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Layout Melhorado ----
st.markdown("### 📌 Resumo Financeiro")

# Exibição de Gastos Fixos e Variáveis de forma mais clara
col1, col2, col3 = st.columns(3)
with col1:
    with st.expander(f"💰 Gastos Fixos: R$ {gastos_fixos:,.2f}"):
        st.dataframe(df_filtrado[df_filtrado["Categoria"] == "Fixo"])

with col2:
    with st.expander(f"📉 Gastos Variáveis: R$ {gastos_variaveis:,.2f}"):
        st.dataframe(df_filtrado[df_filtrado["Categoria"] == "Variável"])

with col3:
    with st.expander(f"📊 Total de Gastos: R$ {total_gastos:,.2f}"):
        st.dataframe(df_filtrado)

st.markdown("---")

# **Cartão de Crédito**
st.subheader("💳 Gastos no Cartão de Crédito")
st.write(f"💳 Total no Cartão de Crédito: **R$ {total_cartao:,.2f}**")
st.write(f"🔹 Fixos: **R$ {fixo_cartao:,.2f}**  |  🔸 Variáveis: **R$ {variavel_cartao:,.2f}**")

# Botão interativo para exibir detalhes do cartão
with st.expander("🔍 Ver detalhes do Cartão"):
    st.dataframe(df_cartao)

st.markdown("---")

# ---- Análises Financeiras ----
st.subheader("📈 Análises Financeiras")

# Gráfico de Gastos por Centro de Custo
df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
fig_centro_custo = px.bar(df_resumo_centro, x="Centro de custo", y="Valor", text_auto=True, title="Gastos por Centro de Custo", height=400)
st.plotly_chart(fig_centro_custo, use_container_width=True)

# Gráfico de Pizza - Distribuição Fixo x Variável
fig_fixo_variavel = px.pie(df_filtrado, names="Categoria", values="Valor", title="Distribuição dos Gastos (Fixo vs Variável)")
st.plotly_chart(fig_fixo_variavel, use_container_width=True)

st.markdown("---")

# **Tabela Completa dos Dados Filtrados**
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)
