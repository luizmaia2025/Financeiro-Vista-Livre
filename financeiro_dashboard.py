import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.dataframe_explorer import dataframe_explorer

# URL pública da planilha (versão CSV)
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Carregar os dados
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR, dtype=str).fillna("")
    df_receber = pd.read_csv(SHEET_URL_RECEBER, dtype=str).fillna("")
    
    # Ajustar colunas
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()
    
    # Conversão de datas
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], errors="coerce", dayfirst=True)
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], errors="coerce", dayfirst=True)
    
    # Tratamento da coluna "Valor"
    for df in [df_pagar, df_receber]:
        df["Valor"] = df["Valor"].astype(str).str.replace(r"[^\d,.-]", "", regex=True).str.replace(",", ".")
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    
    return df_pagar, df_receber

# Carregar os dados
df_pagar, df_receber = load_data()

# Interface no Streamlit
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title('📊 Dashboard Financeiro - Vista Livre 2025')

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro por tipo de data
tipo_data = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

data_coluna = "Data de Vencimento" if tipo_data == "Data de Vencimento" else "Data lançamento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por categoria
categorias = df_pagar["Categoria"].dropna().unique().tolist()
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categorias, default=categorias)

# Filtro por Status
status_opcoes = df_pagar["Status (Pago/Em Aberto)"].dropna().unique().tolist()
status_selecionado = st.sidebar.multiselect("Filtrar por Status:", status_opcoes, default=status_opcoes)

# Filtro por Forma de Pagamento
formas_pagamento = ["Todas"] + df_pagar["Forma de Pagamento"].dropna().unique().tolist()
forma_pagamento_selecionada = st.sidebar.selectbox("Forma de Pagamento:", formas_pagamento)

# Aplicação dos filtros
df_filtrado = df_pagar[
    (df_pagar["Categoria"].isin(categoria_selecionada)) &
    (df_pagar["Status (Pago/Em Aberto)"].isin(status_selecionado)) &
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]
if forma_pagamento_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Forma de Pagamento"] == forma_pagamento_selecionada]

# Exibir métricas
st.subheader("📊 Resumo Financeiro")
col1, col2, col3 = st.columns(3)
col1.metric("Total a Pagar", f"R$ {df_filtrado['Valor'].sum():,.2f}")
col2.metric("Total Fixo", f"R$ {df_filtrado[df_filtrado['Categoria'] == 'Fixo']['Valor'].sum():,.2f}")
col3.metric("Total Variável", f"R$ {df_filtrado[df_filtrado['Categoria'] == 'Variável']['Valor'].sum():,.2f}")
style_metric_cards()

# Exibir dados filtrados
df_explorer = dataframe_explorer(df_filtrado, case=False)
st.dataframe(df_explorer)

# Gráficos
st.subheader("📊 Distribuição das Contas a Pagar")
fig_pagar = px.bar(df_filtrado, x="Categoria", y="Valor", title="Contas a Pagar por Categoria", color="Categoria")
st.plotly_chart(fig_pagar, use_container_width=True)

fig_centro_custo = px.pie(df_filtrado, names="Centro de custo", values="Valor", title="Distribuição por Centro de Custo")
st.plotly_chart(fig_centro_custo, use_container_width=True)

st.success("✅ Dashboard atualizado com sucesso!")
