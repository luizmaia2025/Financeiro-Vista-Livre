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
    df_pagar["Data lançamento"] = pd.to_datetime(df_pagar["Data lançamento"], format="%d/%m/%Y", errors="coerce")
    df_pagar["Data de Vencimento"] = pd.to_datetime(df_pagar["Data de Vencimento"], format="%d/%m/%Y", errors="coerce")
    df_pagar["Data de Pagamento"] = pd.to_datetime(df_pagar["Data de Pagamento"], format="%d/%m/%Y", errors="coerce")

    df_receber["Data Fechamento"] = pd.to_datetime(df_receber["Data Fechamento"], format="%d/%m/%Y", errors="coerce")
    df_receber["Data de Recebimento"] = pd.to_datetime(df_receber["Data de Recebimento"], format="%d/%m/%Y", errors="coerce")
    df_receber["Data de Pagamento"] = pd.to_datetime(df_receber["Data de Pagamento"], format="%d/%m/%Y", errors="coerce")

    # Limpar a coluna "Valor" e converter para numérico
    df_pagar["Valor"] = pd.to_numeric(df_pagar["Valor"].astype(str).str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")
    df_receber["Valor"] = pd.to_numeric(df_receber["Valor"].astype(str).str.replace("R$", "").str.replace(",", "").str.strip(), errors="coerce")

    return df_pagar, df_receber

# Criar o dashboard
st.title("📊 Dashboard Financeiro - Vista Livre 2025")

df_pagar, df_receber = load_data()

if not df_pagar.empty and not df_receber.empty:
    # **Filtros**
    st.sidebar.header("🔍 Filtros")

    categoria_filtro = st.sidebar.multiselect("Filtrar por Categoria:", df_pagar["Categoria"].unique(), default=df_pagar["Categoria"].unique())
    status_filtro = 
