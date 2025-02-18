import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Configuração da Página ----
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

# ---- URL da Planilha Google Sheets ----
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"

# ---- Função para Carregar Dados ----
@st.cache_data(ttl=600)  # Atualiza a cada 10 minutos para evitar cache desatualizado
def load_data():
    try:
        df_pagar = pd.read_csv(SHEET_URL_PAGAR)

        # Corrigir nomes das colunas
        df_pagar.columns = df_pagar.columns.str.strip()

        # Converter colunas de data
        df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors='coerce')
        df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors='coerce')

        # Corrigir valores numéricos
        df_pagar["Valor"] = df_pagar["Valor"].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"], errors='coerce')

        return df_pagar
    except Exception as e:
        st.error(f"❌ Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df_pagar = load_data()

# ---- Sidebar - Filtros ----
st.sidebar.header("📌 Filtros")

# Escolher entre "Data de Lançamento" ou "Data de Vencimento"
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

# Seleção do período
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por Centro de Custo
centro_opcoes = df_pagar["Centro de custo"].dropna().unique()
centro_selecionado = st.sidebar.multiselect("Filtrar por Centro de Custo:", centro_opcoes, default=centro_opcoes)

# Aplicar Filtros para Empresa
df_empresa = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Centro de custo"].isin(centro_selecionado))
]

# ---- Cálculo dos Valores da Empresa ----
total_gastos_empresa = df_empresa["Valor"].sum()
gastos_fixos_empresa = df_empresa[df_empresa["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis_empresa = df_empresa[df_empresa["Categoria"] == "Variável"]["Valor"].sum()

# ---- Cartão de Crédito ----
df_cartao = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim)) &
    (df_pagar["Subtipo"] == "Cartão de crédito")
]

total_cartao_credito = df_cartao["Valor"].sum()
fixo_cartao = df_cartao[df_cartao["Categoria"] == "Fixo"]["Valor"].sum()
variavel_cartao = df_cartao[df_cartao["Categoria"] == "Variável"]["Valor"].sum()

# ---- Botões para abrir e fechar tabelas ----
mostrar_fixos = st.checkbox("🔍 Mostrar Gastos Fixos")
mostrar_variaveis = st.checkbox("🔍 Mostrar Gastos Variáveis")
mostrar_cartao = st.checkbox("💳 Mostrar Gastos no Cartão de Crédito")

# ---- Exibição dos Dados ----
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# **Resumo Financeiro da Empresa**
st.subheader("📌 Resumo Financeiro (Empresa)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Gastos Fixos", f"R$ {gastos_fixos_empresa:,.2f}")
with col2:
    st.metric("💸 Gastos Variáveis", f"R$ {gastos_variaveis_empresa:,.2f}")
with col3:
    st.metric("📊 Total de Gastos", f"R$ {total_gastos_empresa:,.2f}")

if mostrar_fixos:
    st.subheader("📋 Gastos Fixos - Detalhamento")
    st.dataframe(df_empresa[df_empresa["Categoria"] == "Fixo"])

if mostrar_variaveis:
    st.subheader("📋 Gastos Variáveis - Detalhamento")
    st.dataframe(df_empresa[df_empresa["Categoria"] == "Variável"])

st.markdown("---")

# **Cartão de Crédito**
st.subheader("💳 Gastos no Cartão de Crédito")
st.metric("📌 Total no Cartão de Crédito", f"R$ {total_cartao_credito:,.2f}")
st.text(f"📌 Fixos: R$ {fixo_cartao:,.2f}  |  📌 Variáveis: R$ {variavel_cartao:,.2f}")

if mostrar_cartao:
    st.subheader("📋 Detalhamento dos Gastos no Cartão de Crédito")
    st.dataframe(df_cartao)

st.markdown("---")

# ---- Gráficos ----
st.subheader("📈 Análises Financeiras")

# **Gráfico de Gastos por Centro de Custo**
df_resumo_centro = df_empresa.groupby("Centro de custo")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
fig_centro_custo = px.bar(df_resumo_centro, x="Centro de custo", y="Valor", color="Centro de custo",
                          title="Gastos por Centro de Custo", text_auto=True, height=400)
st.plotly_chart(fig_centro_custo, use_container_width=True)

# **Gráfico de Distribuição Fixo x Variável**
col4, col5 = st.columns((2, 1))
with col5:
    fig_fixo_variavel = px.pie(df_empresa, names="Categoria", values="Valor", title="Distribuição de Gastos (Fixo vs Variável)")
    st.plotly_chart(fig_fixo_variavel, use_container_width=True)

st.markdown("---")

# **Tabela de Resumo por Centro de Custo**
st.subheader("📋 Resumo por Centro de Custo")
st.dataframe(df_resumo_centro, hide_index=True, use_container_width=True)

st.markdown("---")

# **Tabela Completa dos Dados Filtrados**
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_empresa)
