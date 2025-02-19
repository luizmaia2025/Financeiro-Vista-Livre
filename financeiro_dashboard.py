import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import altair as alt
import numpy as np
from sklearn.linear_model import LinearRegression
from ydata_profiling import ProfileReport
from streamlit_extras.app_button import app_button
from streamlit_option_menu import option_menu

# ---- Configuração da Página ----
st.set_page_config(page_title="📊 Controle Financeiro - Vista Livre", layout="wide")

# ---- Estilização Global ----
st.markdown(
    """
    <style>
        .css-1d391kg {padding: 10px 20px;}
        .css-1cpxqw2 {margin-bottom: 10px;}
        .stButton>button {
            background-color: #007BFF;
            color: white;
            padding: 8px 20px;
            border-radius: 8px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Menu Lateral ----
menu = option_menu(
    menu_title=None,
    options=["Resumo", "Análises", "Previsões", "Exploração"],
    icons=["clipboard", "bar-chart", "lightbulb", "search"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# ---- Carregar Dados ----
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL_PAGAR)
    df.columns = df.columns.str.strip()
    df["Data lançamento"] = pd.to_datetime(df["Data lançamento"], dayfirst=True, errors='coerce')
    df["Valor"] = pd.to_numeric(df["Valor"].str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors='coerce')
    return df

df_pagar = load_data()

# ---- Filtros ----
st.sidebar.header("🔍 Filtros")
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

# ---- Aplicando Filtros ----
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Seção de Resumo Financeiro ----
if menu == "Resumo":
    st.subheader("💰 Resumo Financeiro")
    col1, col2, col3 = st.columns(3)
    with col1:
        button("Ver Detalhes Fixos")
        st.metric("🏦 Gastos Fixos", f"R$ {df_filtrado[df_filtrado['Categoria'] == 'Fixo']['Valor'].sum():,.2f}")
    with col2:
        button("Ver Detalhes Variáveis")
        st.metric("📉 Gastos Variáveis", f"R$ {df_filtrado[df_filtrado['Categoria'] == 'Variável']['Valor'].sum():,.2f}")
    with col3:
        button("Ver Detalhes Totais")
        st.metric("📊 Total de Gastos", f"R$ {df_filtrado['Valor'].sum():,.2f}")

# ---- Seção de Análises ----
if menu == "Análises":
    st.subheader("📈 Análises Financeiras")
    fig_bar = alt.Chart(df_filtrado).mark_bar().encode(
        x="Valor",
        y="Centro de custo",
        color="Centro de custo"
    ).properties(width=600)
    
    fig_pizza = px.pie(df_filtrado, names="Centro de custo", values="Valor", title="Distribuição % por Centro de Custo", height=300)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.altair_chart(fig_bar, use_container_width=True)
    with col2:
        st.plotly_chart(fig_pizza, use_container_width=True)

# ---- Seção de Previsões ----
if menu == "Previsões":
    st.subheader("🔮 Previsão de Gastos")
    df_pagar['Mês'] = df_pagar["Data lançamento"].dt.month
    X = np.array(df_pagar['Mês']).reshape(-1,1)
    y = df_pagar['Valor']
    modelo = LinearRegression()
    modelo.fit(X, y)
    previsao = modelo.predict(np.array([[13]]))
    st.write(f"🔮 Previsão de gastos para o próximo mês: R$ {previsao[0]:,.2f}")

# ---- Seção de Análise Exploratória ----
if menu == "Exploração":
    st.subheader("🔍 Análise Exploratória")
    report = ProfileReport(df_pagar, explorative=True)
    st.write("Gerando relatório...")
    report.to_file("relatorio_analise.html")
    st.write("📄 [Baixar relatório completo](relatorio_analise.html)")
