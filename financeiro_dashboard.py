import pandas as pd
import streamlit as st
import plotly.express as px

# URL pública da planilha (versão CSV)
SHEET_ID = "1hxeG2XDXR3yVrKNCB9wdgUtY0oX22IjmnDi3iitPboc"
SHEET_URL_PAGAR = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20pagar"
SHEET_URL_RECEBER = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Contas%20a%20receber"

# Carregar os dados das planilhas
@st.cache_data
def load_data():
    df_pagar = pd.read_csv(SHEET_URL_PAGAR)
    df_receber = pd.read_csv(SHEET_URL_RECEBER)
    return df_pagar, df_receber

# Criar o dashboard
st.title('📊 Dashboard Financeiro')

df_pagar, df_receber = load_data()

if not df_pagar.empty and not df_receber.empty:
    # Converter colunas numéricas
    df_pagar['Valor'] = pd.to_numeric(df_pagar['Valor'], errors='coerce')
    df_receber['Valor'] = pd.to_numeric(df_receber['Valor'], errors='coerce')
    
    # Cálculo de totais
    total_pagar = df_pagar['Valor'].sum()
    total_receber = df_receber['Valor'].sum()
    saldo_final = total_receber - total_pagar
    
    st.metric('Total a Pagar', f'R$ {total_pagar:,.2f}')
    st.metric('Total a Receber', f'R$ {total_receber:,.2f}')
    st.metric('Saldo Final', f'R$ {saldo_final:,.2f}', delta=f'R$ {saldo_final:,.2f}')
    
    # Gráfico de Contas a Pagar
    fig_pagar = px.bar(df_pagar, x='Categoria', y='Valor', title='Contas a Pagar por Categoria')
    st.plotly_chart(fig_pagar)
    
    # Gráfico de Contas a Receber
    fig_receber = px.bar(df_receber, x='Categoria', y='Valor', title='Contas a Receber por Categoria')
    st.plotly_chart(fig_receber)
    
    # Insight sobre maiores despesas
    despesas_top = df_pagar.nlargest(5, 'Valor')
    st.subheader('📉 Maiores Contas a Pagar')
    st.table(despesas_top[['Categoria', 'Valor']])
    
    # Insight sobre maiores recebimentos
    recebimentos_top = df_receber.nlargest(5, 'Valor')
    st.subheader('📈 Maiores Contas a Receber')
    st.table(recebimentos_top[['Categoria', 'Valor']])
    
else:
    st.warning('Nenhum dado encontrado. Verifique se a planilha está pública e os nomes das abas estão corretos.')
