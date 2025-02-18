import pandas as pd
import streamlit as st
import plotly.express as px

# 📌 Configuração do Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"  # ID da sua planilha
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# 🚀 Função para carregar dados da planilha
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)
    
    # 🛠 Ajustar nomes de colunas e converter valores
    df_pagar.columns = df_pagar.iloc[0]  # Define a primeira linha como cabeçalho
    df_receber.columns = df_receber.iloc[0]
    df_pagar = df_pagar[1:].reset_index(drop=True)  # Remove a primeira linha duplicada
    df_receber = df_receber[1:].reset_index(drop=True)

    # Converter valores numéricos
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"].str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"].str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")

    # Converter datas
    df_pagar["Data de Lançamento"] = pd.to_datetime(df_pagar["Data de Lançamento"], errors="coerce", dayfirst=True)
    df_receber["Data de Lançamento"] = pd.to_datetime(df_receber["Data de Lançamento"], errors="coerce", dayfirst=True)

    return df_pagar, df_receber

# 🚀 Criar Dashboard no Streamlit
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

df_pagar, df_receber = load_data()

# Verifica se os dados foram carregados
if not df_pagar.empty and not df_receber.empty:
    
    # 🛠 Filtros interativos
    st.sidebar.header("Filtros")

    # 📅 Filtro por Data
    data_inicio = st.sidebar.date_input("Data Inicial", df_pagar["Data de Lançamento"].min())
    data_fim = st.sidebar.date_input("Data Final", df_pagar["Data de Lançamento"].max())

    # 🏢 Filtro por Centro de Custo
    centro_custo = st.sidebar.multiselect("Centro de Custo", df_pagar["Centro de Custo"].dropna().unique(), default=df_pagar["Centro de Custo"].dropna().unique())

    # 📂 Filtro por Categoria (Fixo/Variável)
    categoria = st.sidebar.multiselect("Categoria", df_pagar["Categoria"].dropna().unique(), default=df_pagar["Categoria"].dropna().unique())

    # ✅ Filtrar os dados
    df_filtrado = df_pagar[
        (df_pagar["Data de Lançamento"] >= pd.to_datetime(data_inicio)) &
        (df_pagar["Data de Lançamento"] <= pd.to_datetime(data_fim)) &
        (df_pagar["Centro de Custo"].isin(centro_custo)) &
        (df_pagar["Categoria"].isin(categoria))
    ]

    # 💰 Indicadores financeiros
    total_pagar = df_filtrado["Valor"].sum()
    total_receber = df_receber["Valor"].sum()
    saldo_final = total_receber - total_pagar

    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total a Pagar", f"R$ {total_pagar:,.2f}")
    col2.metric("💰 Total a Receber", f"R$ {total_receber:,.2f}")
    col3.metric("📈 Saldo Final", f"R$ {saldo_final:,.2f}")

    # 📊 Gráficos financeiros
    st.subheader("💡 Contas a Pagar por Centro de Custo")
    fig_pagar = px.bar(df_filtrado, x="Centro de Custo", y="Valor", color="Centro de Custo", title="Distribuição de Despesas")
    st.plotly_chart(fig_pagar)

    st.subheader("💡 Contas Pagas por Categoria")
    fig_categoria = px.pie(df_receber, names="Categoria", values="Valor", title="Proporção de Gastos Pagos")
    st.plotly_chart(fig_categoria)

    # 📅 Exibir tabela filtrada
    st.subheader("📜 Tabela de Lançamentos")
    st.dataframe(df_filtrado)

else:
    st.warning("⚠️ Nenhum dado encontrado! Verifique se a planilha está pública e os nomes das abas estão corretos.")

