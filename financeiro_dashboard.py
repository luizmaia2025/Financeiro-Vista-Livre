import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha do Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Função para carregar os dados
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)

    # Remover espaços extras dos nomes das colunas
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()

    # Converter datas corretamente
    date_columns_pagar = ["Data lançamento", "Data de Vencimento", "Data de Pagamento"]
    date_columns_receber = ["Data Fechamento", "Data de Recebimento", "Data de Pagamento"]

    for col in date_columns_pagar:
        df_pagar[col] = pd.to_datetime(df_pagar[col], format="%d/%m/%Y", errors="coerce")

    for col in date_columns_receber:
        df_receber[col] = pd.to_datetime(df_receber[col], format="%d/%m/%Y", errors="coerce")

    # Limpar e converter a coluna "Valor"
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"].astype(str).str.replace("R$", "", regex=True).str.replace(",", "", regex=True).str.strip(), errors="coerce")
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"].astype(str).str.replace("R$", "", regex=True).str.replace(",", "", regex=True).str.strip(), errors="coerce")

    return df_pagar, df_receber

# Criar o dashboard
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

df_pagar, df_receber = load_data()

if not df_pagar.empty and not df_receber.empty:
    # **Exibir dados brutos para depuração**
    with st.expander("📜 Dados Brutos - Contas a Pagar"):
        st.write(df_pagar.head())

    with st.expander("📜 Dados Brutos - Contas a Receber"):
        st.write(df_receber.head())

    # **Filtros**
    st.sidebar.header("🔍 Filtros")

    # Opção para escolher entre Data de Lançamento ou Data de Vencimento
    data_tipo = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

    # Definir qual coluna será usada como base de data
    data_coluna_pagar = "Data lançamento" if data_tipo == "Data de Lançamento" else "Data de Vencimento"

    categoria_filtro = st.sidebar.multiselect("Filtrar por Categoria:", df_pagar["Categoria"].dropna().unique(), default=df_pagar["Categoria"].dropna().unique())
    status_filtro = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", df_pagar["Status (Pago/Em Aberto)"].dropna().unique(), default=df_pagar["Status (Pago/Em Aberto)"].dropna().unique())
    forma_pagamento_filtro = st.sidebar.multiselect("Forma de Pagamento:", df_pagar["Forma de Pagamento"].dropna().unique(), default=df_pagar["Forma de Pagamento"].dropna().unique())

    data_inicio = st.sidebar.date_input(f"{data_tipo} Inicial", df_pagar[data_coluna_pagar].min())
    data_fim = st.sidebar.date_input(f"{data_tipo} Final", df_pagar[data_coluna_pagar].max())

    # Aplicar filtros
    df_pagar_filtrado = df_pagar[
        (df_pagar["Categoria"].isin(categoria_filtro)) &
        (df_pagar["Status (Pago/Em Aberto)"].isin(status_filtro)) &
        (df_pagar["Forma de Pagamento"].isin(forma_pagamento_filtro)) &
        (df_pagar[data_coluna_pagar].between(pd.Timestamp(data_inicio), pd.Timestamp(data_fim)))
    ]

    df_receber_filtrado = df_receber[
        df_receber["Data Fechamento"].between(pd.Timestamp(data_inicio), pd.Timestamp(data_fim))
    ]

    # **Verificar se os filtros eliminaram todos os dados**
    if df_pagar_filtrado.empty:
        st.warning(f"⚠ Nenhuma conta a pagar encontrada entre {data_inicio} e {data_fim}.")
    if df_receber_filtrado.empty:
        st.warning(f"⚠ Nenhuma conta a receber encontrada entre {data_inicio} e {data_fim}.")

    # **Métricas Financeiras**
    total_pagar = df_pagar_filtrado["Valor"].sum()
    total_receber = df_receber_filtrado["Valor"].sum()
    saldo_final = total_receber - total_pagar

    st.metric("💸 Total a Pagar", f'R$ {total_pagar:,.2f}')
    st.metric("💰 Total a Receber", f'R$ {total_receber:,.2f}')
    st.metric("📈 Saldo Final", f'R$ {saldo_final:,.2f}', delta=f'R$ {saldo_final:,.2f}')

    # **Gráficos**
    st.subheader("📊 Distribuição das Contas a Pagar")
    if not df_pagar_filtrado.empty:
        fig_pagar = px.bar(df_pagar_filtrado, x="Categoria", y="Valor", color="Centro de custo", title=f"Contas a Pagar por Categoria ({data_tipo})")
        st.plotly_chart(fig_pagar)
    else:
        st.warning("⚠ Não há dados suficientes para gerar o gráfico de Contas a Pagar.")

    st.subheader("📊 Distribuição das Contas a Receber")
    if not df_receber_filtrado.empty:
        fig_receber = px.bar(df_receber_filtrado, x="Categoria", y="Valor", color="Cliente", title="Contas a Receber por Categoria")
        st.plotly_chart(fig_receber)
    else:
        st.warning("⚠ Não há dados suficientes para gerar o gráfico de Contas a Receber.")

    # **Maiores Despesas**
    if not df_pagar_filtrado.empty:
        despesas_top = df_pagar_filtrado.nlargest(5, "Valor")
        st.subheader("📉 Maiores Contas a Pagar")
        st.table(despesas_top[["Fornecedor", "Produto", "Valor"]])
    else:
        st.warning("⚠ Não há despesas para exibir.")

    # **Maiores Recebimentos**
    if not df_receber_filtrado.empty:
        recebimentos_top = df_receber_filtrado.nlargest(5, "Valor")
        st.subheader("📈 Maiores Contas a Receber")
        st.table(recebimentos_top[["Cliente", "Descrição", "Valor"]])
    else:
        st.warning("⚠ Não há recebimentos para exibir.")

else:
    st.warning("⚠ Nenhum dado encontrado. Verifique se a planilha está pública e os nomes das abas estão corretos.")
