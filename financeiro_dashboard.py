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
    df_pagar.columns = df_pagar.columns.str.strip()
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')
    return df_pagar

# Carregar os dados
df_pagar = load_data()

st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# Sidebar - Filtros Interativos
st.sidebar.header("🔍 Filtros")
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por Centro de Custo com opção de selecionar todos
centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
selecionar_todos = st.sidebar.checkbox("Selecionar Todos os Centros de Custo", value=True)
centro_selecionado = centro_opcoes if selecionar_todos else st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Cálculo dos Valores ----
df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
df_fixo = df_filtrado[df_filtrado["Categoria"] == "Fixo"].groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
df_variavel = df_filtrado[df_filtrado["Categoria"] == "Variável"].groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)

# ---- Gráficos ----

## 1️⃣ Gráfico de Gastos por Centro de Custo
st.subheader("📊 Gastos por Centro de Custo")

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    st.subheader("📊 Gastos Totais")
    fig_centro_custo = px.bar(df_resumo_centro, 
                              y="Centro de custo", 
                              x="Valor", 
                              text_auto=True, 
                              orientation="h",
                              title="Gastos por Centro de Custo",
                              height=400)
    st.plotly_chart(fig_centro_custo, use_container_width=True)

with col2:
    st.subheader("📊 % por Centro de Custo")
    fig_pizza_centro_custo = px.pie(df_resumo_centro, 
                                    names="Centro de custo", 
                                    values="Valor", 
                                    title="Percentual dos Gastos",
                                    height=400)
    st.plotly_chart(fig_pizza_centro_custo, use_container_width=True)

with col3:
    centro_selecionado_grafico = st.selectbox("Clique para ver detalhes:", df_resumo_centro["Centro de custo"])
    if centro_selecionado_grafico:
        st.subheader(f"📋 Detalhes: {centro_selecionado_grafico}")
        df_detalhado = df_filtrado[df_filtrado["Centro de custo"] == centro_selecionado_grafico]
        st.dataframe(df_detalhado, use_container_width=True)

## 2️⃣ Gráfico de Gastos Fixos por Centro de Custo
st.subheader("🏦 Gastos Fixos por Centro de Custo")

col4, col5, col6 = st.columns([2, 1, 2])

with col4:
    st.subheader("📊 Gastos Fixos")
    fig_fixo = px.bar(df_fixo, 
                      y="Centro de custo", 
                      x="Valor", 
                      text_auto=True, 
                      orientation="h",
                      title="Gastos Fixos por Centro de Custo",
                      height=400)
    st.plotly_chart(fig_fixo, use_container_width=True)

with col5:
    st.subheader("📊 % por Centro de Custo")
    fig_pizza_fixo = px.pie(df_fixo, 
                            names="Centro de custo", 
                            values="Valor", 
                            title="Percentual dos Gastos Fixos",
                            height=400)
    st.plotly_chart(fig_pizza_fixo, use_container_width=True)

with col6:
    centro_fixo_grafico = st.selectbox("Clique para ver detalhes dos Fixos:", df_fixo["Centro de custo"])
    if centro_fixo_grafico:
        st.subheader(f"📋 Detalhes Fixos: {centro_fixo_grafico}")
        df_detalhado_fixo = df_filtrado[(df_filtrado["Centro de custo"] == centro_fixo_grafico) & (df_filtrado["Categoria"] == "Fixo")]
        st.dataframe(df_detalhado_fixo, use_container_width=True)

## 3️⃣ Gráfico de Gastos Variáveis por Centro de Custo
st.subheader("📉 Gastos Variáveis por Centro de Custo")

col7, col8, col9 = st.columns([2, 1, 2])

with col7:
    st.subheader("📊 Gastos Variáveis")
    fig_variavel = px.bar(df_variavel, 
                          y="Centro de custo", 
                          x="Valor", 
                          text_auto=True, 
                          orientation="h",
                          title="Gastos Variáveis por Centro de Custo",
                          height=400)
    st.plotly_chart(fig_variavel, use_container_width=True)

with col8:
    st.subheader("📊 % por Centro de Custo")
    fig_pizza_variavel = px.pie(df_variavel, 
                                names="Centro de custo", 
                                values="Valor", 
                                title="Percentual dos Gastos Variáveis",
                                height=400)
    st.plotly_chart(fig_pizza_variavel, use_container_width=True)

with col9:
    centro_variavel_grafico = st.selectbox("Clique para ver detalhes dos Variáveis:", df_variavel["Centro de custo"])
    if centro_variavel_grafico:
        st.subheader(f"📋 Detalhes Variáveis: {centro_variavel_grafico}")
        df_detalhado_variavel = df_filtrado[(df_filtrado["Centro de custo"] == centro_variavel_grafico) & (df_filtrado["Categoria"] == "Variável")]
        st.dataframe(df_detalhado_variavel, use_container_width=True)
