import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração do Tema ----
st.set_page_config(page_title="📊 Dashboard Financeiro - Vista Livre", layout="wide")

# ---- Estilização Global ----
st.markdown(
    """
    <style>
        /* Ajustes gerais para espaçamento e alinhamento */
        .css-1d391kg {padding: 10px 20px;}
        .css-1cpxqw2 {margin-bottom: 10px;}

        /* Ajustes dos botões */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 8px 20px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
            font-size: 14px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }

        /* Melhorando as tabelas */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }

        /* Ajuste para mobile */
        @media screen and (max-width: 768px) {
            .st-emotion-cache-16txtl3 {width: 100% !important;}
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- URL pública da planilha no Google Sheets ----
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_pagar.columns = df_pagar.columns.str.strip()
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')
    return df_pagar

df_pagar = load_data()

st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# ---- Sidebar - Filtros Interativos ----
st.sidebar.header("🔍 Filtros")
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

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
    if st.button("Ver Detalhes Fixos"):
        st.dataframe(df_filtrado[df_filtrado["Categoria"] == "Fixo"], use_container_width=True)
    st.metric(label="🏦 Gastos Fixos", value=f"R$ {gastos_fixos:,.2f}")

with col2:
    if st.button("Ver Detalhes Variáveis"):
        st.dataframe(df_filtrado[df_filtrado["Categoria"] == "Variável"], use_container_width=True)
    st.metric(label="📉 Gastos Variáveis", value=f"R$ {gastos_variaveis:,.2f}")

with col3:
    if st.button("Ver Detalhes Totais"):
        st.dataframe(df_filtrado, use_container_width=True)
    st.metric(label="📊 Total de Gastos", value=f"R$ {total_gastos:,.2f}")

# ---- Gráficos ----
st.subheader("📈 Análises Financeiras")

df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)

def gerar_graficos(df, titulo):
    st.subheader(titulo)
    col1, col2 = st.columns([2, 1])

    with col1:
        fig_bar = px.bar(df, y="Centro de custo", x="Valor", text_auto=True, orientation="h", title=f"{titulo}", height=400, color="Centro de custo")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pizza = px.pie(df, names="Centro de custo", values="Valor", title=f"Percentual {titulo}", height=400)
        st.plotly_chart(fig_pizza, use_container_width=True)

## Gráficos
gerar_graficos(df_resumo_centro, "📊 Gastos por Centro de Custo")
gerar_graficos(df_filtrado[df_filtrado["Categoria"] == "Fixo"].groupby("Centro de custo")["Valor"].sum().reset_index(), "🏦 Gastos Fixos por Centro de Custo")
gerar_graficos(df_filtrado[df_filtrado["Categoria"] == "Variável"].groupby("Centro de custo")["Valor"].sum().reset_index(), "📉 Gastos Variáveis por Centro de Custo")
