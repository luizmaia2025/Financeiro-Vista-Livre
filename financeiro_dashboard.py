import streamlit as st
import pandas as pd
import plotly.express as px

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
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')
    df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')
    return df_pagar

df_pagar = load_data()

st.title("📊 Controle Financeiro - Vista Livre")

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

# ---- Cartão de Crédito ----
st.subheader("💳 Gastos no Cartão de Crédito")
if st.button("Ver Detalhes do Cartão"):
    st.dataframe(df_cartao, use_container_width=True)
st.metric(label="💳 Total no Cartão de Crédito", value=f"R$ {total_cartao:,.2f}")
st.text(f"🔹 Fixos: R$ {fixo_cartao:,.2f}  |  🔸 Variáveis: R$ {variavel_cartao:,.2f}")

# ---- Função para Gerar Gráficos ----
def gerar_graficos(df, titulo):
    st.subheader(titulo)
    col1, col2 = st.columns([2, 1])

    with col1:
        fig_bar = px.bar(df, y="Centro de custo", x="Valor", text_auto=True, orientation="h", title=f"{titulo}", height=400, color="Centro de custo")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pizza = px.pie(df, names="Centro de custo", values="Valor", title=f"Percentual {titulo}", height=400)
        st.plotly_chart(fig_pizza, use_container_width=True)

# ---- Gráficos ----
st.subheader("📈 Análises Financeiras")

# ---- Filtros Dinâmicos Adicionais ----
st.sidebar.header("📅 Período de Análise")
anos_disponiveis = df_pagar["Data lançamento"].dt.year.unique()
ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", sorted(anos_disponiveis, reverse=True))

meses_disponiveis = df_pagar[df_pagar["Data lançamento"].dt.year == ano_selecionado]["Data lançamento"].dt.month.unique()
mes_selecionado = st.sidebar.selectbox("Selecione o Mês:", sorted(meses_disponiveis))

# Filtrar por Ano e Mês Selecionado
df_filtrado = df_filtrado[
    (df_filtrado["Data lançamento"].dt.year == ano_selecionado) &
    (df_filtrado["Data lançamento"].dt.month == mes_selecionado)
]

# ---- Comparação Mensal ----
st.subheader("📈 Comparação de Gastos Mensais")
df_mensal = df_filtrado.groupby(df_filtrado["Data lançamento"].dt.month)["Valor"].sum().reset_index()
fig_mensal = px.line(df_mensal, x="Data lançamento", y="Valor", markers=True, title="Tendência de Gastos Mensais")
st.plotly_chart(fig_mensal, use_container_width=True)

# ---- Comparação por Categoria ----
st.subheader("📊 Gastos por Categoria")
df_categoria = df_filtrado.groupby("Categoria")["Valor"].sum().reset_index()
fig_categoria = px.bar(df_categoria, x="Categoria", y="Valor", color="Categoria", text_auto=True, title="Distribuição de Gastos por Categoria")
st.plotly_chart(fig_categoria, use_container_width=True)

# ---- Exportação de Dados ----
st.sidebar.subheader("📥 Exportar Dados")
csv = df_filtrado.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("Baixar CSV", data=csv, file_name="dados_financeiros.csv", mime="text/csv")

# ---- Painel de Alertas Financeiros ----
st.subheader("⚠️ Alertas Financeiros")
media_gastos = df_pagar["Valor"].mean()
if total_gastos > media_gastos * 1.2:
    st.warning(f"🚨 Atenção! Seus gastos neste mês ({total_gastos:,.2f}) estão **20% acima da média histórica**!")
elif total_gastos < media_gastos * 0.8:
    st.success(f"🎉 Excelente! Seus gastos estão **20% abaixo da média histórica**!")



df_resumo_centro = df_filtrado.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)

gerar_graficos(df_resumo_centro, "📊 Gastos por Centro de Custo")
gerar_graficos(df_filtrado[df_filtrado["Categoria"] == "Fixo"].groupby("Centro de custo")["Valor"].sum().reset_index(), "🏦 Gastos Fixos por Centro de Custo")
gerar_graficos(df_filtrado[df_filtrado["Categoria"] == "Variável"].groupby("Centro de custo")["Valor"].sum().reset_index(), "📉 Gastos Variáveis por Centro de Custo")
