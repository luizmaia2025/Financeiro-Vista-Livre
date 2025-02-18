import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha no Google Sheets
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Carregar os dados das planilhas
@st.cache_data
def @st.cache_data

def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)

    # Padronizar os nomes das colunas para evitar problemas de formatação
    df_pagar.columns = df_pagar.columns.str.strip()
    df_receber.columns = df_receber.columns.str.strip()

    # Converter colunas de datas corretamente
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], errors="coerce")
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], errors="coerce")
    df_pagar["Data de Pagamento"] = pd.to_datetime(df_pagar["Data de Pagamento"], errors="coerce")

    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], errors="coerce")
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], errors="coerce")
    df_receber["Data de Pagamento"] = pd.to_datetime(df_receber["Data de Pagamento"], errors="coerce")

    # Tratar valores inválidos antes da conversão para float
    def limpar_valor(valor):
        """Função para limpar valores, remover 'R$', espaços e caracteres inválidos."""
        try:
            if isinstance(valor, str):  
                valor = valor.replace("R$", "").replace(",", "").strip()
            return float(valor)  # Converter para float
        except:
            return 0.0  # Se não for possível converter, retorna 0

    df_pagar["Valor"] = df_pagar["Valor"].apply(limpar_valor)
    df_receber["Valor"] = df_receber["Valor"].apply(limpar_valor)

    return df_pagar, df_receber


# Criar o dashboard
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title('📊 Dashboard Financeiro - Vista Livre 2025')

# Carregar os dados
df_pagar, df_receber = load_data()

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro por Data (Lançamento ou Vencimento)
data_coluna = st.sidebar.radio("Filtrar por:", ["Data de Lançamento", "Data de Vencimento"])

# Ajustar a coluna para correspondência correta
if data_coluna == "Data de Lançamento":
    data_coluna = "Data lançamento"
else:
    data_coluna = "Data de Vencimento"

# Garantir que a coluna esteja no formato datetime
df_pagar[data_coluna] = pd.to_datetime(df_pagar[data_coluna], errors='coerce')

# Definir a data mínima e máxima sem erros
data_min = df_pagar[data_coluna].min()
data_max = df_pagar[data_coluna].max()

if pd.isna(data_min) or pd.isna(data_max):
    data_min = pd.Timestamp.today().date()
    data_max = pd.Timestamp.today().date()

# Criar inputs de data com valores padrão
data_inicio = st.sidebar.date_input("Data Inicial", data_min)
data_fim = st.sidebar.date_input("Data Final", data_max)

# Filtrar os dados com base no intervalo de datas
df_pagar_filtrado = df_pagar[(df_pagar[data_coluna] >= pd.to_datetime(data_inicio)) & 
                             (df_pagar[data_coluna] <= pd.to_datetime(data_fim))]

# Filtro por Categoria
categorias = df_pagar_filtrado["Categoria"].dropna().unique().tolist()
categoria_selecionada = st.sidebar.multiselect("Filtrar por Categoria:", categorias, default=categorias)

# Aplicar filtro de categoria
df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Categoria"].isin(categoria_selecionada)]

# Filtro por Status (Pago/Em Aberto)
status_opcoes = df_pagar_filtrado["Status (Pago/Em Aberto)"].dropna().unique().tolist()
status_selecionado = st.sidebar.multiselect("Filtrar por Status (Pago/Em Aberto):", status_opcoes, default=status_opcoes)

# Aplicar filtro de Status
df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Status (Pago/Em Aberto)"].isin(status_selecionado)]

# Filtro por Forma de Pagamento
formas_pagamento = df_pagar_filtrado["Forma de Pagamento"].dropna().unique().tolist()
forma_pagamento_selecionada = st.sidebar.selectbox("Forma de Pagamento:", ["Todas"] + formas_pagamento)

# Aplicar filtro de Forma de Pagamento (caso não seja "Todas")
if forma_pagamento_selecionada != "Todas":
    df_pagar_filtrado = df_pagar_filtrado[df_pagar_filtrado["Forma de Pagamento"] == forma_pagamento_selecionada]

# Exibir Métricas Financeiras
total_pagar = df_pagar_filtrado["Valor"].sum()
total_receber = df_receber["Valor"].sum()
saldo_final = total_receber - total_pagar

st.markdown("### 🔹 Resumo Financeiro")
col1, col2, col3 = st.columns(3)
col1.metric("💰 Total a Pagar", f'R$ {total_pagar:,.2f}')
col2.metric("📥 Total a Receber", f'R$ {total_receber:,.2f}')
col3.metric("🔹 Saldo Final", f'R$ {saldo_final:,.2f}', delta=f'R$ {saldo_final:,.2f}')

# Exibir os dados filtrados
st.markdown("### 📋 Dados Filtrados - Contas a Pagar")
st.dataframe(df_pagar_filtrado)

# Gráfico de Contas a Pagar por Categoria
st.markdown("### 📊 Distribuição das Contas a Pagar")
fig_pagar = px.bar(df_pagar_filtrado, x="Categoria", y="Valor", title="Contas a Pagar por Categoria", color="Categoria")
st.plotly_chart(fig_pagar, use_container_width=True)

# Gráfico de Contas a Receber por Categoria
st.markdown("### 📊 Distribuição das Contas a Receber")
fig_receber = px.bar(df_receber, x="Categoria", y="Valor", title="Contas a Receber por Categoria", color="Categoria")
st.plotly_chart(fig_receber, use_container_width=True)

# Maiores despesas e recebimentos
st.markdown("### 🔍 Maiores Contas a Pagar")
st.table(df_pagar_filtrado.nlargest(5, 'Valor')[["Categoria", "Valor"]])

st.markdown("### 🔍 Maiores Contas a Receber")
st.table(df_receber.nlargest(5, 'Valor')[["Categoria", "Valor"]])

st.sidebar.markdown("---")
st.sidebar.markdown("📊 *Dashboard Financeiro - Vista Livre 2025*")
