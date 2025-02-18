import pandas as pd
import streamlit as st
import plotly.express as px

# 🔹 Configuração da Página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# 🔹 Função para Carregar Dados
@st.cache_data
def load_data():
    url = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc/edit?gid=0#gid=0/pub?output=csv"
    df = pd.read_csv(url)

    # Ajustar nomes das colunas para evitar espaços invisíveis
    df.columns = df.columns.str.strip()

    # 🔹 Convertendo valores numéricos corretamente
    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # 🔹 Convertendo datas
    df["Data de Lançamento"] = pd.to_datetime(df["Data de Lançamento"], format="%d/%m/%Y", errors="coerce")
    df["Data de Vencimento"] = pd.to_datetime(df["Data de Vencimento"], format="%d/%m/%Y", errors="coerce")

    return df

# 🔹 Carregar os dados
try:
    df = load_data()
    st.success("Dados carregados com sucesso! ✅")
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# 🔹 Filtros Interativos na Sidebar
st.sidebar.header("🔍 Filtros")
categoria_filter = st.sidebar.multiselect("Filtrar por Categoria", options=df["Categoria"].unique(), default=df["Categoria"].unique())
status_filter = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto)", options=df["Status (Pago/Em Aberto)"].unique(), default=df["Status (Pago/Em Aberto)"].unique())

# 🔹 Aplicar Filtros
df_filtered = df[df["Categoria"].isin(categoria_filter) & df["Status (Pago/Em Aberto)"].isin(status_filter)]

# 🔹 Indicadores Principais
total_gastos = df_filtered["Valor"].sum()
media_gastos = df_filtered["Valor"].mean()
gastos_fixos = df_filtered[df_filtered["Categoria"] == "Fixo"]["Valor"].sum()
gastos_variaveis = df_filtered[df_filtered["Categoria"] == "Variável"]["Valor"].sum()

# 🔹 Exibição de Indicadores
st.markdown("## 📊 **Visão Geral Financeira**")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total de Gastos", f"R$ {total_gastos:,.2f}")
col2.metric("📉 Média de Gastos", f"R$ {media_gastos:,.2f}")
col3.metric("📌 Gastos Fixos", f"R$ {gastos_fixos:,.2f}")
col4.metric("📌 Gastos Variáveis", f"R$ {gastos_variaveis:,.2f}")

# 🔹 Gráfico de Gastos por Categoria
st.markdown("## 📊 **Distribuição das Contas a Pagar**")
fig = px.bar(df_filtered, x="Categoria", y="Valor", color="Categoria", barmode="group", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# 🔹 Gráfico de Gastos ao Longo do Tempo
st.markdown("## 📅 **Tendência de Gastos ao Longo do Tempo**")
df_trend = df_filtered.groupby("Data de Vencimento")["Valor"].sum().reset_index()
fig_trend = px.line(df_trend, x="Data de Vencimento", y="Valor", markers=True)
st.plotly_chart(fig_trend, use_container_width=True)

# 🔹 Tabela de Gastos
st.markdown("## 📋 **Lista de Contas a Pagar**")
st.dataframe(df_filtered)

# 🔹 Botões de Controle
st.markdown("### 🔄 **Ações Rápidas**")
col1, col2, col3 = st.columns(3)
if col1.button("🔄 Atualizar Dados"):
    st.experimental_rerun()
if col2.button("📅 Ver Próximos Vencimentos"):
    df_proximos = df_filtered[df_filtered["Data de Vencimento"] > pd.Timestamp.today()]
    st.dataframe(df_proximos)
if col3.button("💾 Baixar Relatório"):
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV", data=csv, file_name="Relatorio_Financeiro.csv", mime="text/csv")
