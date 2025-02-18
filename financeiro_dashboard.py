import streamlit as st
import pandas as pd
import plotly.express as px

# 🔹 Configuração inicial da página
st.set_page_config(page_title="Dashboard Financeiro - Vista Livre", layout="wide")

# 🔹 URLS das planilhas no Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# 🔹 Cache para evitar recarregamento desnecessário
@st.cache_data
def load_data():
    """Carrega e processa os dados financeiros"""
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)

    # 🔹 Padronizar nomes das colunas
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()

    # 🔹 Converter datas corretamente
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], dayfirst=True, errors="coerce")
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], dayfirst=True, errors="coerce")
    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], dayfirst=True, errors="coerce")
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], dayfirst=True, errors="coerce")

    # 🔹 Corrigir valores financeiros
    def converter_valor(valor):
        """Função para limpar e converter valores"""
        return pd.to_numeric(
            valor.astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )

    df_pagar["Valor"] = converter_valor(df_pagar["Valor"])
    df_receber["Valor"] = converter_valor(df_receber["Valor"])

    return df_pagar, df_receber

# 🔹 Carregar os dados
df_pagar, df_receber = load_data()

# 🔹 Título do Dashboard
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

# 🔹 Sidebar - Filtros Interativos
st.sidebar.header("🔍 Filtros")

# Escolher entre "Data de Lançamento" ou "Data de Vencimento"
data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

# Seleção do período
data_coluna = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"
data_inicio = st.sidebar.date_input("Data Inicial", df_pagar[data_coluna].min())
data_fim = st.sidebar.date_input("Data Final", df_pagar[data_coluna].max())

# Filtro por Categoria
categoria_opcoes = ["Todos"] + list(df_pagar["Categoria"].dropna().unique())
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categoria_opcoes, default=["Todos"])

# Filtro por Status
status_opcoes = ["Todos"] + list(df_pagar["Status (Pago/Em Aberto)"].dropna().unique())
status_selecionado = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default=["Todos"])

# 🔹 Aplicação dos filtros
df_filtrado = df_pagar[
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

if "Todos" not in categoria_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]

if "Todos" not in status_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Status (Pago/Em Aberto)"].isin(status_selecionado)]

# ---- Exibir Tabela Filtrada ----
st.subheader("📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# ---- Criar Gráficos ----
st.subheader("📈 Distribuição das Contas a Pagar")

# Gráfico de Valores por Categoria
fig_categoria = px.bar(
    df_filtrado, 
    x="Categoria", 
    y="Valor", 
    color="Categoria", 
    title="Total de Gastos por Categoria",
    labels={"Valor": "Total Gasto (R$)"}
)
st.plotly_chart(fig_categoria, use_container_width=True)

# Gráfico de Valores por Status
fig_status = px.pie(
    df_filtrado, 
    names="Status (Pago/Em Aberto)", 
    values="Valor", 
    title="Status das Contas a Pagar",
    labels={"Valor": "Total (R$)"}
)
st.plotly_chart(fig_status, use_container_width=True)

# 🔹 Resumo Financeiro
st.sidebar.header("📊 Resumo")

total_gastos = df_filtrado["Valor"].sum()
media_gastos = df_filtrado["Valor"].mean()

st.sidebar.metric(label="💰 Total de Gastos", value=f"R$ {total_gastos:,.2f}")
st.sidebar.metric(label="📊 Média de Gastos", value=f"R$ {media_gastos:,.2f}")

# 🔹 Relatórios Adicionais
st.subheader("📉 Relatórios Financeiros")

# Fluxo de Caixa Mensal
df_pagar["Mês"] = df_pagar["Data de Vencimento"].dt.strftime("%Y-%m")
df_receber["Mês"] = df_receber["Data de Recebimento"].dt.strftime("%Y-%m")

df_fluxo = pd.DataFrame({
    "Mês": sorted(df_pagar["Mês"].dropna().unique()),
    "Total Contas a Pagar": df_pagar.groupby("Mês")["Valor"].sum(),
    "Total Contas a Receber": df_receber.groupby("Mês")["Valor"].sum(),
})

fig_fluxo = px.line(
    df_fluxo, 
    x="Mês", 
    y=["Total Contas a Pagar", "Total Contas a Receber"],
    title="📈 Fluxo de Caixa Mensal",
    markers=True
)
st.plotly_chart(fig_fluxo, use_container_width=True)

# 🔹 Conclusão
st.markdown("✅ **Relatórios completos para controle financeiro estratégico!**")

