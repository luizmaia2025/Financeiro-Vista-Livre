import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import altair as alt
from datetime import datetime

# ---- Configuração da Página ----
st.set_page_config(page_title="📊 Controle Financeiro - Vista Livre", layout="wide")

# ---- Estilização Global (CSS) ----
st.markdown(
    """
    <style>
        /* Ajuste do layout responsivo */
        .css-1d391kg {padding: 10px 20px;}
        .css-1cpxqw2 {margin-bottom: 10px;}

        /* Melhorando botões */
        .stButton>button {
            background-color: #007BFF;
            color: white;
            padding: 8px 20px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
            font-size: 14px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }

        /* Melhorando tabelas */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }

        /* Ajuste do layout responsivo para gráficos */
        @media screen and (max-width: 768px) {
            .st-emotion-cache-16txtl3 {width: 100% !important;}
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- URL da Planilha no Google Sheets ----
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_pagar.columns = df_pagar.columns.str.strip()

    # Correção na conversão de datas
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], errors="coerce")
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], errors="coerce")

    # Remover valores inválidos
    df_pagar = df_pagar.dropna(subset=["Data lançamento", "Data de Vencimento"])

    # Corrigir formatação de valores monetários
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

    return df_pagar

df_pagar = load_data()

st.title("📊 Controle Financeiro - Vista Livre")

# ---- Sidebar - Filtros Interativos ----
st.sidebar.header("🔍 Filtros")
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

# Definir valores padrão seguros
data_min = df_pagar[data_coluna].min()
data_max = df_pagar[data_coluna].max()

if pd.isna(data_min) or pd.isna(data_max):
    data_min = datetime(2023, 1, 1)  # Data segura de fallback
    data_max = datetime(2025, 12, 31)

data_inicio = st.sidebar.date_input("Data Inicial", data_min)
data_fim = st.sidebar.date_input("Data Final", data_max)

centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
selecionar_todos = st.sidebar.checkbox("Selecionar Todos os Centros de Custo", value=True)
centro_selecionado = centro_opcoes if selecionar_todos else st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Cálculo dos Valores ----
total_gastos = df_filtrado["Valor"].sum()
gastos_fixos = df_filtrado[df_filtrado["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis = df_filtrado[df_filtrado["Categoria"] == "Variável"]["Valor"].sum()

df_cartao = df_filtrado[df_filtrado["Subtipo"] == "Cartão de crédito"]
total_cartao = df_cartao["Valor"].sum()
fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Resumo Financeiro ----
st.subheader("💰 Resumo Financeiro")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏦 Gastos Fixos", value=f"R$ {gastos_fixos:,.2f}")

with col2:
    st.metric(label="📉 Gastos Variáveis", value=f"R$ {gastos_variaveis:,.2f}")

with col3:
    st.metric(label="📊 Total de Gastos", value=f"R$ {total_gastos:,.2f}")

# ---- Cartão de Crédito ----
st.subheader("💳 Gastos no Cartão de Crédito")
st.metric(label="💳 Total no Cartão de Crédito", value=f"R$ {total_cartao:,.2f}")
st.text(f"🔹 Fixos: R$ {fixo_cartao:,.2f}  |  🔸 Variáveis: R$ {variavel_cartao:,.2f}")

# ---- Gráficos ----
st.subheader("📈 Análises Financeiras")

df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)

# Gráfico de barras refinado com Altair
bar_chart = alt.Chart(df_resumo_centro).mark_bar().encode(
    x=alt.X("Valor:Q", title="Valor"),
    y=alt.Y("Centro de custo:N", title="Centro de Custo", sort='-x'),
    color="Centro de custo:N"
).properties(title="📊 Gastos por Centro de Custo", height=400)

st.altair_chart(bar_chart, use_container_width=True)

# Gráfico de pizza refinado com Seaborn
st.subheader("📊 Percentual de Gastos por Centro de Custo")
fig, ax = plt.subplots(figsize=(5, 5))
sns.set_palette("pastel")
ax.pie(df_resumo_centro["Valor"], labels=df_resumo_centro["Centro de custo"], autopct="%1.1f%%")
st.pyplot(fig)
