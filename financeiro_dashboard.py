import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# 📌 ID da Planilha do Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"

# URLs das abas da planilha
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# 🔄 Função para carregar os dados
@st.cache_data
def load_data():
    try:
        # Leitura dos dados
        df_pagar = pd.read_csv(SHEET_URL_PAGAR)
        df_receber = pd.read_csv(SHEET_URL_RECEBER)

        # Padronização dos nomes das colunas
        df_pagar.columns = df_pagar.columns.str.strip()
        df_receber.columns = df_receber.columns.str.strip()

        # Conversão de datas
        df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], errors='coerce')
        df_pagar["Data de Lançamento"] = pd.to_datetime(df_pagar["Data de Lançamento"], errors='coerce')
        df_receber["Data de Vencimento"] = pd.to_datetime(df_receber["Data de Vencimento"], errors='coerce')

        # Conversão de valores monetários
        df_pagar["Valor"] = (
            df_pagar["Valor"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(",", ".")
            .astype(float)
        )
        df_receber["Valor"] = (
            df_receber["Valor"].astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(",", ".")
            .astype(float)
        )

        return df_pagar, df_receber

    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

# 🚀 Carregar os dados
df_pagar, df_receber = load_data()

# 📌 Se não houver dados, exibir aviso
if df_pagar.empty or df_receber.empty:
    st.warning("⚠️ Os dados não foram carregados. Verifique a URL e as permissões da planilha!")
    st.stop()

# 🛠️ Filtros Interativos
st.sidebar.header("🔎 Filtros")
tipo_data = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
categoria_filtro = st.sidebar.multiselect("Filtrar por Categoria:", df_pagar["Categoria"].dropna().unique(), default=df_pagar["Categoria"].dropna().unique())
status_filtro = st.sidebar.multiselect("Filtrar por Status:", df_pagar["Status (Pago/Em Aberto)"].dropna().unique(), default=df_pagar["Status (Pago/Em Aberto)"].dropna().unique())
forma_pagamento = st.sidebar.selectbox("Forma de Pagamento:", ["Todas"] + list(df_pagar["Forma de Pagamento"].dropna().unique()))
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[tipo_data].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[tipo_data].max())

# 🔍 Filtragem dos dados
df_pagar_filtrado = df_pagar[
    (df_pagar[tipo_data] >= pd.to_datetime(data_inicio)) & 
    (df_pagar[tipo_data] <= pd.to_datetime(data_fim)) & 
    (df_pagar["Categoria"].isin(categoria_filtro)) & 
    (df_pagar["Status (Pago/Em Aberto)"].isin(status_filtro))
]

if forma_pagamento != "Todas":
    df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Forma de Pagamento"] == forma_pagamento]

# 📊 Cálculos Financeiros
total_gastos = df_pagar_filtrado["Valor"].sum()
media_gastos = df_pagar_filtrado["Valor"].mean()
total_receber = df_receber["Valor"].sum()
saldo_liquido = total_receber - total_gastos

# 🏦 Indicadores Financeiros
st.markdown("## 📊 Resumo Financeiro")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total de Gastos", f"R$ {total_gastos:,.2f}")
col2.metric("📉 Média de Gastos", f"R$ {media_gastos:,.2f}")
col3.metric("📈 Total de Contas a Receber", f"R$ {total_receber:,.2f}")
col4.metric("💵 Saldo Líquido", f"R$ {saldo_liquido:,.2f}")

# 📊 Gráficos
st.markdown("## 📊 Distribuição das Contas a Pagar")
fig = px.bar(df_pagar_filtrado, x="Categoria", y="Valor", color="Categoria", title="Total de Gastos por Categoria")
st.plotly_chart(fig, use_container_width=True)

st.markdown("## 📈 Evolução dos Gastos ao Longo do Tempo")
df_pagar_filtrado["Mês"] = df_pagar_filtrado[tipo_data].dt.to_period("M")
fig_tendencia = px.line(df_pagar_filtrado.groupby("Mês")["Valor"].sum().reset_index(), x="Mês", y="Valor", markers=True, title="Tendência de Gastos")
st.plotly_chart(fig_tendencia, use_container_width=True)

st.markdown("## 🔄 Comparação de Gastos e Receitas")
df_fluxo = pd.DataFrame({"Tipo": ["Gastos", "Recebimentos"], "Valor": [total_gastos, total_receber]})
fig_fluxo = px.bar(df_fluxo, x="Tipo", y="Valor", color="Tipo", text="Valor", title="Fluxo Financeiro")
st.plotly_chart(fig_fluxo, use_container_width=True)

st.markdown("## 📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_pagar_filtrado)
