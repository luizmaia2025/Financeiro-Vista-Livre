import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha do Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Carregar os dados das planilhas
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)

    # Definir primeira linha como cabeçalho e remover duplicações
    df_pagar.columns = df_pagar.iloc[0]
    df_receber.columns = df_receber.iloc[0]
    df_pagar = df_pagar[1:].reset_index(drop=True)
    df_receber = df_receber[1:].reset_index(drop=True)

    # Converter datas
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], format="%d/%m/%Y", errors="coerce")
    df_receber["Data lançamento"] = pd.to_datetime(df_receber["Data lançamento"], format="%d/%m/%Y", errors="coerce")

    # Converter valores numéricos
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"].str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"].str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")

    return df_pagar, df_receber

# Criar o dashboard
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

df_pagar, df_receber = load_data()

if not df_pagar.empty and not df_receber.empty:
    # **Filtros**
    st.sidebar.header("Filtros")

    # Filtro por data
    data_min = df_pagar["Data lançamento"].min()
    data_max = df_pagar["Data lançamento"].max()
    data_inicio, data_fim = st.sidebar.date_input("Selecione o período", [data_min, data_max])

    # Filtro por categoria (Fixo/Variável)
    categorias = df_pagar["Categoria"].unique().tolist()
    categoria_selecionada = st.sidebar.multiselect("Categoria", categorias, default=categorias)

    # Filtro por centro de custo
    centros_custo = df_pagar["Centro de custo"].unique().tolist()
    centro_selecionado = st.sidebar.multiselect("Centro de Custo", centros_custo, default=centros_custo)

    # Filtro por fornecedor
    fornecedores = df_pagar["Fornecedor"].unique().tolist()
    fornecedor_selecionado = st.sidebar.multiselect("Fornecedor", fornecedores, default=fornecedores)

    # Filtro por status
    status_opcoes = df_pagar["Status (Pago/Em Aberto)"].unique().tolist()
    status_selecionado = st.sidebar.multiselect("Status", status_opcoes, default=status_opcoes)

    # Aplicar filtros na base de Contas a Pagar
    df_pagar_filtrado = df_pagar[
        (df_pagar["Data lançamento"] >= pd.to_datetime(data_inicio)) &
        (df_pagar["Data lançamento"] <= pd.to_datetime(data_fim)) &
        (df_pagar["Categoria"].isin(categoria_selecionada)) &
        (df_pagar["Centro de custo"].isin(centro_selecionado)) &
        (df_pagar["Fornecedor"].isin(fornecedor_selecionado)) &
        (df_pagar["Status (Pago/Em Aberto)"].isin(status_selecionado))
    ]

    # Aplicar filtros na base de Contas a Receber
    df_receber_filtrado = df_receber[
        (df_receber["Data lançamento"] >= pd.to_datetime(data_inicio)) &
        (df_receber["Data lançamento"] <= pd.to_datetime(data_fim))
    ]

    # **Indicadores financeiros**
    total_pagar = df_pagar_filtrado["Valor"].sum()
    total_receber = df_receber_filtrado["Valor"].sum()
    saldo_final = total_receber - total_pagar

    st.subheader("📌 Indicadores Financeiros")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total a Pagar", f"R$ {total_pagar:,.2f}")
    col2.metric("Total a Receber", f"R$ {total_receber:,.2f}")
    col3.metric("Saldo Final", f"R$ {saldo_final:,.2f}", delta=f"R$ {saldo_final:,.2f}")

    # **Gráficos**
    st.subheader("📊 Análises Financeiras")

    # Gráfico de Contas a Pagar por Categoria
    fig_pagar = px.bar(df_pagar_filtrado, x="Categoria", y="Valor", color="Categoria",
                       title="Contas a Pagar por Categoria", text_auto=True)
    st.plotly_chart(fig_pagar, use_container_width=True)

    # Gráfico de Contas a Pagar por Centro de Custo
    fig_custo = px.pie(df_pagar_filtrado, names="Centro de custo", values="Valor",
                        title="Distribuição das Despesas por Centro de Custo")
    st.plotly_chart(fig_custo, use_container_width=True)

    # Gráfico de Contas a Receber por Categoria
    fig_receber = px.bar(df_receber_filtrado, x="Categoria", y="Valor", color="Categoria",
                         title="Contas a Receber por Categoria", text_auto=True)
    st.plotly_chart(fig_receber, use_container_width=True)

    # **Maiores despesas**
    st.subheader("📉 Maiores Contas a Pagar")
    despesas_top = df_pagar_filtrado.nlargest(5, "Valor")
    st.table(despesas_top[["Fornecedor", "Centro de custo", "Produto", "Valor"]])

    # **Maiores recebimentos**
    st.subheader("📈 Maiores Contas a Receber")
    recebimentos_top = df_receber_filtrado.nlargest(5, "Valor")
    st.table(recebimentos_top[["Fornecedor", "Produto", "Valor"]])

else:
    st.warning("⚠ Nenhum dado encontrado. Verifique se a planilha está pública e os nomes das abas estão corretos.")
