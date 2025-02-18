import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração do Layout Moderno ----
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
        }
        .stApp {
            background-color: #ffffff;
        }
        .stMetric {
            padding: 10px;
            border-radius: 8px;
            color: black;
            text-align: center;
        }
        .stMarkdown {
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# ---- URL do Google Sheets ----
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

# ---- Carregar Dados ----
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)

    # Padronizar os nomes das colunas
    df_pagar.columns = df_pagar.columns.str.strip()

    # Converter datas
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')

    # Converter valores corretamente
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    return df_pagar

df_pagar = load_data()

# ---- Sidebar - Filtros ----
st.sidebar.header("🔍 Filtros")

# Filtro por data
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtros interativos
categoria_opcoes = ["Todos"] + list(df_pagar["Categoria"].dropna().unique())
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default="Todos")

centro_opcoes = ["Todos"] + list(df_pagar["Centro de custo"].dropna().unique())
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default="Todos")

tipo_opcoes = ["Todos"] + list(df_pagar["Tipo"].dropna().unique())
tipo_selecionado = st.sidebar.multiselect("Filtrar por Tipo:", tipo_opcoes, default="Todos")

subtipo_opcoes = ["Todos"] + list(df_pagar["Subtipo"].dropna().unique())
subtipo_selecionado = st.sidebar.multiselect("Filtrar por Subtipo:", subtipo_opcoes, default="Todos")

# Aplicar Filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]
if "Todos" not in centro_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Centro de custo"].isin(centro_selecionado)]
if "Todos" not in tipo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(tipo_selecionado)]
if "Todos" not in subtipo_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Subtipo"].isin(subtipo_selecionado)]

# ---- Cálculos Financeiros ----
gastos_totais = df_filtrado["Valor"].sum()
gastos_fixos = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()

# ---- Cartão de Crédito ----
df_cartao = df_filtrado[df_filtrado["Tipo"] == "Cartão de crédito"]
cartao_credito_total = df_cartao["Valor"].sum()
cartao_credito_fixo = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
cartao_credito_variavel = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Layout do Dashboard ----
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

col1, col2, col3 = st.columns(3)
col1.metric("🏛 Gastos Fixos", f"R$ {gastos_fixos:,.2f}")
col2.metric("🧾 Gastos Variáveis", f"R$ {gastos_variaveis:,.2f}")
col3.metric("💰 Total de Gastos", f"R$ {gastos_totais:,.2f}")

st.divider()

# ---- Cartão de Crédito ----
st.subheader("💳 Gastos no Cartão de Crédito")
st.metric("💳 Total no Cartão de Crédito", f"R$ {cartao_credito_total:,.2f}")
st.markdown(f"🔹 **Fixos:** R$ {cartao_credito_fixo:,.2f} | 🟣 **Variáveis:** R$ {cartao_credito_variavel:,.2f}")

st.divider()

# ---- Gráficos ----
st.subheader("📈 Análises Financeiras")

df_centro_custo = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
col_graf1, col_tabela = st.columns(2)

fig_centro_custo = px.bar(df_centro_custo, x="Valor", y="Centro de custo", orientation="h",
                          title="Gastos por Centro de Custo", text_auto=".2s")
col_graf1.plotly_chart(fig_centro_custo, use_container_width=True)

col_tabela.write("🔍 **Resumo por Centro de Custo**")
col_tabela.dataframe(df_centro_custo, hide_index=True, use_container_width=True)

st.divider()

fig_fixo_variavel = px.pie(df_filtrado, names="Categoria", values="Valor", title="Distribuição dos Gastos (Fixo vs Variável)")
st.plotly_chart(fig_fixo_variavel, use_container_width=True)

st.divider()

# ---- Exibir Tabela Filtrada ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado, hide_index=True, use_container_width=True)
