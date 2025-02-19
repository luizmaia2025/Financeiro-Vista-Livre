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

# Aplicar Filtros no DataFrame geral da empresa
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Cálculo dos Valores ----
gastos_fixos = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()
total_gastos = df_filtrado["Valor"].sum()

# ---- Cálculo dos Valores do Cartão de Crédito ----
df_cartao = df_filtrado[df_filtrado["Subtipo"] == "Cartão de crédito"]
total_cartao = df_cartao["Valor"].sum()
fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Layout ----
st.subheader("📌 Resumo Financeiro")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"💰 **Gastos Fixos**: R$ {gastos_fixos:,.2f}")
    if st.button("Ver Detalhes Fixos"):
        st.dataframe(df_filtrado[df_filtrado["Categoria"] == "Fixo"], use_container_width=True)

with col2:
    st.markdown(f"📉 **Gastos Variáveis**: R$ {gastos_variaveis:,.2f}")
    if st.button("Ver Detalhes Variáveis"):
        st.dataframe(df_filtrado[df_filtrado["Categoria"] == "Variável"], use_container_width=True)

with col3:
    st.markdown(f"📊 **Total de Gastos**: R$ {total_gastos:,.2f}")
    if st.button("Ver Detalhes Totais"):
        st.dataframe(df_filtrado, use_container_width=True)

st.markdown("---")

# **Cartão de Crédito**
st.subheader("💳 Gastos no Cartão de Crédito")
st.write(f"💳 Total no Cartão de Crédito: **R$ {total_cartao:,.2f}**")
st.write(f"🔹 Fixos: **R$ {fixo_cartao:,.2f}**  |  🔸 Variáveis: **R$ {variavel_cartao:,.2f}**")

# Botão interativo para exibir detalhes do cartão
if st.button("🔍 Ver detalhes do Cartão"):
    st.dataframe(df_cartao, use_container_width=True)

st.markdown("---")

# ---- Análises Financeiras ----
st.subheader("📈 Análises Financeiras")

# Criar DataFrame de Resumo por Centro de Custo
df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)

# Criar colunas para posicionamento dos gráficos
col_grafico1, col_grafico2 = st.columns(2)

# Gráfico de Barras com Interatividade
with col_grafico1:
    st.subheader("📊 Gastos por Centro de Custo")
    fig_centro_custo = px.bar(df_resumo_centro, 
                              x="Centro de custo", 
                              y="Valor", 
                              text_auto=True, 
                              title="Gastos por Centro de Custo", 
                              height=400)
    
    # Criar uma seleção dinâmica
    centro_selecionado_grafico = st.selectbox("Clique para ver detalhes:", df_resumo_centro["Centro de custo"])

    # Mostrar tabela ao selecionar um centro de custo
    if centro_selecionado_grafico:
        st.subheader(f"📋 Detalhes: {centro_selecionado_grafico}")
        df_detalhado = df_filtrado[df_filtrado["Centro de custo"] == centro_selecionado_grafico]
        st.dataframe(df_detalhado, use_container_width=True)

    st.plotly_chart(fig_centro_custo, use_container_width=True)

# Gráfico de Pizza ao lado
with col_grafico2:
    st.subheader("📊 Distribuição % por Centro de Custo")
    fig_pizza_centro_custo = px.pie(df_resumo_centro, 
                                    names="Centro de custo", 
                                    values="Valor", 
                                    title="Distribuição Percentual dos Gastos",
                                    height=400)
    st.plotly_chart(fig_pizza_centro_custo, use_container_width=True)

st.markdown("---")

# **Tabela Completa dos Dados Filtrados**
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)
