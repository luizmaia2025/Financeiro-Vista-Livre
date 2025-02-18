import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração do Layout ----
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

# ---- URL da Planilha ----
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

# ---- Cache para otimização ----
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)

    # Padronizar colunas
    df_pagar.columns = df_pagar.columns.str.strip()

    # Converter datas
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')

    # Formatar valores
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    # Padronização para evitar erros nos filtros
    df_pagar["Categoria"] = df_pagar["Categoria"].str.strip().str.capitalize()
    df_pagar["Subtipo"] = df_pagar["Subtipo"].str.strip().str.lower()
    df_pagar["Centro de custo"] = df_pagar["Centro de custo"].str.strip()

    return df_pagar

# ---- Carregar os Dados ----
df_pagar = load_data()

# ---- 📌 CALCULAR OS TOTAIS DA EMPRESA (ANTES DOS FILTROS) ----
total_gastos_empresa = df_pagar["Valor"].sum()
gastos_fixos_empresa = df_pagar[df_pagar["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis_empresa = df_pagar[df_pagar["Categoria"] == "Variável"]["Valor"].sum()

# ---- SIDEBAR: Filtros ----
st.sidebar.title("🎛️ Filtros")

# Filtro por Data
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtros Dinâmicos
categoria_opcoes = ["Todos"] + sorted(df_pagar["Categoria"].dropna().unique().tolist())
subtipo_opcoes = ["Todos"] + sorted(df_pagar["Subtipo"].dropna().unique().tolist())
centro_custo_opcoes = ["Todos"] + sorted(df_pagar["Centro de custo"].dropna().unique().tolist())

categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")
subtipo_selecionado = st.sidebar.multiselect("Filtrar por Subtipo:", subtipo_opcoes, default="Todos")
centro_custo_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_custo_opcoes, default="Todos")

# ---- 📌 APLICAR FILTROS (SEM ALTERAR TOTAIS GERAIS) ----
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]

if "Todos" not in subtipo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Subtipo"].isin(subtipo_selecionado)]

if "Todos" not in centro_custo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Centro de custo"].isin(centro_custo_selecionado)]

# ---- 📌 CÁLCULO DOS VALORES FILTRADOS (INDEPENDENTE DOS VALORES DA EMPRESA) ----
total_gastos_filtro = df_filtrado["Valor"].sum()
gastos_fixos_filtro = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis_filtro = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()

# ---- 📌 CARTÃO DE CRÉDITO (INDEPENDENTE DOS VALORES GERAIS) ----
df_cartao = df_pagar[df_pagar["Subtipo"] == "cartão de crédito"]
cartao_credito_total = df_cartao["Valor"].sum()
cartao_credito_fixo = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
cartao_credito_variavel = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- 📊 DASHBOARD ----
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

col1, col2, col3 = st.columns(3)
col1.metric("🏦 Gastos Fixos", f"R$ {gastos_fixos_empresa:,.2f}")  
col2.metric("📊 Gastos Variáveis", f"R$ {gastos_variaveis_empresa:,.2f}")  
col3.metric("💰 Total de Gastos", f"R$ {total_gastos_empresa:,.2f}")  

st.subheader("💳 Gastos no Cartão de Crédito")
st.metric("💳 Total no Cartão de Crédito", f"R$ {cartao_credito_total:,.2f}")
st.markdown(f"🔹 **Fixos:** R$ {cartao_credito_fixo:,.2f} | 🟣 **Variáveis:** R$ {cartao_credito_variavel:,.2f}")

# ---- 📊 GRÁFICOS ----
st.subheader("📊 Análises Financeiras")

col_graf1, col_tabela = st.columns([2, 1])

# 📊 Gasto por Centro de Custo
df_custo = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
fig_centro_custo = px.bar(df_custo, x="Centro de custo", y="Valor", title="Gastos por Centro de Custo", text_auto=".2f")
col_graf1.plotly_chart(fig_centro_custo, use_container_width=True)

# 📝 Tabela Resumo
col_tabela.write("📋 **Resumo por Centro de Custo**")
col_tabela.dataframe(df_custo, hide_index=True, use_container_width=True)

st.divider()

# 📊 Distribuição Fixo x Variável
fig_fixo_variavel = px.pie(df_filtrado, names="Categoria", values="Valor", title="Distribuição dos Gastos (Fixo vs Variável)")
st.plotly_chart(fig_fixo_variavel, use_container_width=True)

st.divider()

# 📊 Gráfico por Subtipo
fig_subtipo = px.bar(df_filtrado, x="Subtipo", y="Valor", title="Gastos por Subtipo", color="Subtipo", text_auto=".2f")
st.plotly_chart(fig_subtipo, use_container_width=True)

# ---- 📋 TABELA DE DADOS ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado, use_container_width=True)
