import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha (versão CSV)
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Função para carregar os dados
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR, dtype=str).fillna("")
    df_receber = pd.read_csv(SHEET_URL_RECEBER, dtype=str).fillna("")

    # Padronizar nomes das colunas
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()

    # Converter colunas de data
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], errors="coerce", dayfirst=True)
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], errors="coerce", dayfirst=True)
    
    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], errors="coerce", dayfirst=True)
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], errors="coerce", dayfirst=True)

    # Corrigir a conversão da coluna "Valor"
    for df in [df_pagar, df_receber]:
        df["Valor"] = (
            df["Valor"]
            .astype(str)
            .str.replace(r"[^\d,.-]", "", regex=True)  # Remove caracteres não numéricos
            .str.replace(",", ".", regex=False)  # Troca vírgula por ponto
        )
        
        # Converter para float, substituindo erros por 0
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)

    return df_pagar, df_receber

# Carregar os dados
df_pagar, df_receber = load_data()

# Interface no Streamlit
st.title('📊 Dashboard Financeiro - Vista Livre 2025')

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro por tipo de data (Lançamento ou Vencimento)
tipo_data = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

# Filtro por categoria
categorias = df_pagar["Categoria"].dropna().unique().tolist()
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categorias, default=categorias)

# Filtro por Status (Pago/Em Aberto)
status_opcoes = df_pagar["Status (Pago/Em Aberto)"].dropna().unique().tolist()
status_selecionado = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default=status_opcoes)

# Filtro por Forma de Pagamento
formas_pagamento = ["Todas"] + df_pagar["Forma de Pagamento"].dropna().unique().tolist()
forma_pagamento_selecionada = st.sidebar.selectbox("Forma de Pagamento:", formas_pagamento)

# Filtro por Data Inicial e Final
data_coluna = "Data de Vencimento" if tipo_data == "Data de Vencimento" else "Data lançamento"
data_min = df_pagar[data_coluna].min()
data_max = df_pagar[data_coluna].max()

data_inicio = st.sidebar.date_input("Data Inicial", data_min)
data_fim = st.sidebar.date_input("Data Final", data_max)

# Aplicação dos filtros
df_filtrado = df_pagar[
    (df_pagar["Categoria"].isin(categoria_selecionada)) &
    (df_pagar["Status (Pago/Em Aberto)"].isin(status_selecionado)) &
    (df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) &
    (df_pagar[data_coluna] <= pd.to_datetime(data_fim))
]

# Filtro pela forma de pagamento
if forma_pagamento_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Forma de Pagamento"] == forma_pagamento_selecionada]

# Exibir dados filtrados
st.subheader("📑 Dados Filtrados - Contas a Pagar")
st.dataframe(df_filtrado)

# Métricas Financeiras
st.subheader("📊 Resumo Financeiro")
total_pagar = df_filtrado["Valor"].sum()
st.metric("Total a Pagar", f"R$ {total_pagar:,.2f}")

# Gráfico de distribuição por categoria
st.subheader("📊 Distribuição das Contas a Pagar")
fig_pagar = px.bar(df_filtrado, x="Categoria", y="Valor", title="Contas a Pagar por Categoria")
st.plotly_chart(fig_pagar)

# **Contas a Receber**
st.subheader("📑 Dados Brutos - Contas a Receber")
st.dataframe(df_receber)

# Total a receber
total_receber = df_receber["Valor"].sum()
st.metric("Total a Receber", f"R$ {total_receber:,.2f}")

# Gráfico de distribuição de contas a receber
fig_receber = px.bar(df_receber, x="Categoria", y="Valor", title="Contas a Receber por Categoria")
st.plotly_chart(fig_receber)

# **Saldo Final**
saldo_final = total_receber - total_pagar
st.metric("💰 Saldo Final", f"R$ {saldo_final:,.2f}", delta=f"R$ {saldo_final:,.2f}")

st.success("✅ Dashboard atualizado com sucesso!")
