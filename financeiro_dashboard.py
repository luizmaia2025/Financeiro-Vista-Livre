import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha (versão CSV)
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Carregar os dados das planilhas
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)
    
    # Garantir que os nomes das colunas estão corretos
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()
    
    # Converter colunas de data
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], format="%d/%m/%Y", errors="coerce")
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], format="%d/%m/%Y", errors="coerce")
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], format="%d/%m/%Y", errors="coerce")
    
    # Ajustar valores numéricos
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"].astype(str).str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"].astype(str).str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")
    
    return df_pagar, df_receber

# Criar o dashboard
st.title('📊 Dashboard Financeiro - Vista Livre 2025')

df_pagar, df_receber = load_data()

# Filtros
st.sidebar.header("🔍 Filtros")

# Escolha entre Data de Lançamento e Data de Vencimento
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"], index=1)

# Filtro de Categoria
categorias = df_pagar["Categoria"].dropna().unique()
filtro_categoria = st.sidebar.multiselect("Filtrar por Categoria:", categorias, default=categorias)

# Filtro de Status
status_opcoes = df_pagar["Status (Pago/Em Aberto)"].dropna().unique()
filtro_status = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default=status_opcoes)

# Filtro de Forma de Pagamento
formas_pagamento = df_pagar["Forma de Pagamento"].dropna().unique()
filtro_forma = st.sidebar.selectbox("Forma de Pagamento:", ["Todas"] + list(formas_pagamento))

# Filtrando por Data Inicial e Final
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_min, data_max = df_pagar[data_coluna].min(), df_pagar[data_coluna].max()
data_inicio = st.sidebar.date_input("Data Inicial", data_min)
data_fim = st.sidebar.date_input("Data Final", data_max)

# Aplicando filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Categoria"].isin(filtro_categoria)) &
    (df_pagar["Status (Pago/Em Aberto)"].isin(filtro_status))
]
if filtro_forma != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Forma de Pagamento"] == filtro_forma]

# Mostrar os dados filtrados
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# Cálculo de totais
if not df_filtrado.empty:
    total_pagar = df_filtrado["Valor"].sum()
    st.metric("Total Filtrado a Pagar", f'R$ {total_pagar:,.2f}')

    # Gráfico de Contas a Pagar
    fig_pagar = px.bar(df_filtrado, x='Categoria', y='Valor', title='Contas a Pagar por Categoria')
    st.plotly_chart(fig_pagar)
else:
    st.warning("Nenhum dado encontrado para os filtros aplicados.")
