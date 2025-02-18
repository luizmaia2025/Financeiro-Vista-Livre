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
    df_pagar = pd.read_csv(SHEET_URL_PAGAR, dtype=str).fillna("")
    df_receber = pd.read_csv(SHEET_URL_RECEBER, dtype=str).fillna("")
    
    # Converter datas
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], errors="coerce", dayfirst=True)
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], errors="coerce", dayfirst=True)
    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], errors="coerce", dayfirst=True)
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], errors="coerce", dayfirst=True)
    
    # Converter valores para numérico
    df_pagar["Valor"] = df_pagar["Valor"].str.replace("R$", "").str.replace(",", "").str.strip()
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors="coerce")
    df_receber["Valor"] = df_receber["Valor"].str.replace("R$", "").str.replace(",", "").str.strip()
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"], errors="coerce")
    
    return df_pagar, df_receber

# Criar o dashboard
st.title('📊 Dashboard Financeiro - Vista Livre 2025')

df_pagar, df_receber = load_data()

# Opções de filtro
data_filtro = st.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"], index=1)
categoria_filtro = st.multiselect("Filtrar por Categoria:", df_pagar["Categoria"].unique())
status_filtro = st.multiselect("Filtrar por Status (Pago/Em Aberto):", df_pagar["Status (Pago/Em Aberto)"].unique())
forma_pagamento_filtro = st.selectbox("Forma de Pagamento:", ["Todas"] + df_pagar["Forma de Pagamento"].unique().tolist())

data_inicial = st.date_input("Data Inicial", min_value=df_pagar["Data de Vencimento"].min(), max_value=df_pagar["Data de Vencimento"].max())
data_final = st.date_input("Data Final", min_value=data_inicial, max_value=df_pagar["Data de Vencimento"].max())

# Aplicar filtros
filtro_data = "Data lançamento" if data_filtro == "Data de Lançamento" else "Data de Vencimento"
df_pagar_filtrado = df_pagar[(df_pagar[filtro_data] >= pd.to_datetime(data_inicial)) & (df_pagar[filtro_data] <= pd.to_datetime(data_final))]
if categoria_filtro:
    df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Categoria"].isin(categoria_filtro)]
if status_filtro:
    df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Status (Pago/Em Aberto)"].isin(status_filtro)]
if forma_pagamento_filtro != "Todas":
    df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Forma de Pagamento"] == forma_pagamento_filtro]

# Exibir os dados filtrados
st.subheader("📄 Dados Filtrados - Contas a Pagar")
st.dataframe(df_pagar_filtrado)

# Gráficos
if not df_pagar_filtrado.empty:
    fig_pagar = px.bar(df_pagar_filtrado, x="Categoria", y="Valor", title="Distribuição das Contas a Pagar", color="Categoria")
    st.plotly_chart(fig_pagar)
    
    fig_custo_fixo = px.pie(df_pagar_filtrado[df_pagar_filtrado["Categoria"] == "Fixo"], values="Valor", names="Centro de custo", title="Distribuição dos Custos Fixos")
    st.plotly_chart(fig_custo_fixo)
    
    fig_custo_variavel = px.pie(df_pagar_filtrado[df_pagar_filtrado["Categoria"] == "Variável"], values="Valor", names="Centro de custo", title="Distribuição dos Custos Variáveis")
    st.plotly_chart(fig_custo_variavel)
else:
    st.warning("Nenhum dado encontrado para os filtros aplicados.")
