import streamlit as st
import pandas as pd
import plotly.express as px
from numerize.numerize import numerize
from query import *
import os
import time
from streamlit_option_menu import option_menu

# Configuração da página (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Minimiza a barra lateral por padrão
)

# --- GERENCIAMENTO DE ESTADO DA NAVEGAÇÃO ---
if "aba_atual" not in st.session_state:
    st.session_state.aba_atual = "Home"

# Capturar clique do menu via parâmetros de URL
params = st.query_params
if "page" in params:
    st.session_state.aba_atual = params["page"]

# --- FORÇAR TEMA AZUL ESCURO E MENU SUPERIOR ---
st.markdown("""
<style>
    /* Ocultar menus e rodapés padrões do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Remover completamente o botão e espaço da barra lateral */
    section[data-testid="stSidebar"] {display: none;}
    button[data-testid="sidebar-collapse-button"] {display: none;}

    /* Fundo geral da página */
    .stApp {
        background-color: #001122 !important;
        color: #ffffff !important;
    }

    /* Cores de texto globais */
    h1, h2, h3, h4, h5, h6, p, label, .stSubheader {
        color: #ffffff !important;
    }

    /* BARRA DE NAVEGAÇÃO SUPERIOR HTML */
    .navbar {
        background-color: #0c1929;
        border: 1px solid #154c79;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .navbar-brand {
        font-size: 20px;
        font-weight: bold;
        color: #ffffff;
    }
    .navbar-menu {
        display: flex;
        gap: 12px;
    }
    .nav-item {
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 8px 18px;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    .nav-item:hover {
        background-color: #154c79;
        color: #00ffcc !important;
    }
    .nav-active {
        background-color: #154c79;
        color: #00ffcc !important;
        border-bottom: 2px solid #00ffcc;
    }

    /* Caixas de Métricas Responsivas */
    div[data-testid="stMetricSimpleContainer"], div[data-testid="stMetricContainer"] {
        background-color: #0c1929 !important;
        border: 1px solid #154c79 !important;
        padding: 12px !important; 
        border-radius: 10px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
        margin-bottom: 10px !important; 
    }

    div[data-testid="stMetricLabel"] > div { color: #ffffff !important; font-size: 0.9rem !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.5rem !important; }

    /* Estilização para deixar caixas de seleção elegantes no tema escuro */
    div[data-baseweb="select"] {
        background-color: #0c1929 !important;
        color: white !important;
    }

    /* Estilo específico para envolver a imagem da logo */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
        width: 100%;
    }

    /* AJUSTES DE CENTRALIZAÇÃO PARA CELULAR */
    @media (max-width: 768px) {
        .navbar {
            flex-direction: column;
            gap: 12px;
            text-align: center;
            justify-content: center !important;
        }
        .navbar-menu {
            flex-direction: column;
            width: 100%;
            gap: 8px;
        }
        .nav-item {
            display: block;
            width: 100%;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }
        .stMarkdown, .stText, h1, h2, h3, p, label {
            text-align: center !important;
            width: 100%;
        }
        div[data-baseweb="select"], .stMultiSelect, .stSelectbox {
            width: 100% !important;
            max-width: 400px;
            margin: 0 auto !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Imagem centralizada maior (mudou de 150 para 250)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("data/logo1.webp", width=250)
st.markdown('</div>', unsafe_allow_html=True)

# --- RENDERIZAÇÃO DO MENU SUPERIOR (HTML) ---
home_class = "nav-item nav-active" if st.session_state.aba_atual == "Home" else "nav-item"
graficos_class = "nav-item nav-active" if st.session_state.aba_atual == "Gráficos" else "nav-item"

st.markdown(f"""
    <div class="navbar">
        <div class="navbar-brand">📊 Insurance Descriptive Analytics</div>
        <div class="navbar-menu">
            <a class="{home_class}" href="?page=Home" target="_self">Início</a>
            <a class="{graficos_class}" href="?page=Gráficos" target="_self">Gráficos</a>
        </div>
    </div>
""", unsafe_allow_html=True)

## 1. Buscar dados e criar o DataFrame base
result = view_all_data()
df = pd.DataFrame(result, columns=["COL 1", "COL 2", "COL 3", "Investment", "Rating", "BusinessType"])

# --- FILTROS POSICIONADOS NA PARTE DE CIMA DA TELA ---
st.markdown("### 🎛️ Filtros de Pesquisa")
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

with col_filtro1:
    region = st.selectbox("Selecione a Região", options=df["COL 1"].unique())

# Filtragem intermediária imediata
df_filtrado_por_regiao = df[df["COL 1"] == region]

with col_filtro2:
    opcoes_localizacao = df_filtrado_por_regiao["COL 2"].unique()
    location = st.multiselect("Select Location", options=opcoes_localizacao, default=opcoes_localizacao)

df_filtrado_por_local = df_filtrado_por_regiao[df_filtrado_por_regiao["COL 2"].isin(location)]

with col_filtro3:
    opcoes_construcao = df_filtrado_por_local["COL 3"].unique()
    construction = st.multiselect("Select Construction", options=opcoes_construcao, default=opcoes_construcao)

# 2. Aplicação final dos filtros
df_selection = df_filtrado_por_local[df_filtrado_por_local["COL 3"].isin(construction)]

st.markdown("""___""")

# --- PROTEÇÃO CONTRA CONTEÚDO VAZIO ---
if df_selection.empty:
    st.warning("⚠️ Nenhum dado encontrado para a combinação de filtros selecionada.")
    st.stop()

# --- TRATAMENTO E CÁLCULO DAS MÉTRICAS ---
df_selection["Investment"] = pd.to_numeric(df_selection["Investment"], errors='coerce').fillna(0)
df_selection["Rating"] = pd.to_numeric(df_selection["Rating"], errors='coerce').fillna(0)

total_investment = float(df_selection["Investment"].sum())
mode_series = df_selection["Investment"].mode()
investment_mode = float(mode_series.iloc[0]) if not mode_series.empty else 0.0
investment_mean = float(df_selection["Investment"].mean()) if not df_selection.empty else 0.0
investment_median = float(df_selection["Investment"].median()) if not df_selection.empty else 0.0
rating_sum = float(df_selection["Rating"].sum())

# --- EXIBIÇÃO CONDICIONAL DE CONTEÚDO ---
if st.session_state.aba_atual == "Home":
    # 1. Recalcula as métricas dinâmicas com base no DataFrame filtrado (df_selection)
    if not df_selection.empty:
        try:
            total_investment = int(df_selection["Investment"].sum())
            investment_mean = round(df_selection["Investment"].mean(), 2)
            investment_median = df_selection["Investment"].median()

            # Tratamento para a Moda (retorna o primeiro valor se houver mais de um)
            mode_series = df_selection["Investment"].mode()
            investment_mode = mode_series.iloc[0] if not mode_series.empty else 0

            rating_sum = df_selection["Rating"].sum()
        except Exception:
            total_investment = 0
            investment_mean = 0.0
            investment_median = 0.0
            investment_mode = 0.0
            rating_sum = 0.0

    # Adicione a exibição dos seus blocos/gráficos da página Home daqui para baixo
        # Adicione a exibição dos seus blocos/gráficos da página Home daqui para baixo
        st.subheader("Métricas Principais")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Investment", numerize(total_investment))
        col2.metric("Investment Mean", numerize(investment_mean))
        col3.metric("Rating Sum", numerize(rating_sum))

        # --- SEÇÃO DE GRÁFICOS DA PÁGINA HOME ---
        st.markdown("### 📊 Análise Gráfica")
        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            st.subheader("Investimento por Tipo de Negócio")
            df_invest_business = df_selection.groupby("BusinessType")["Investment"].sum().reset_index()
            fig_barras = px.bar(
                df_invest_business,
                x="BusinessType",
                y="Investment",
                template="plotly_dark",
                color_discrete_sequence=["#00ffcc"]
            )
            fig_barras.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_barras, use_container_width=True)

        with col_grafico2:
            st.subheader("Distribuição por Rating")
            df_rating = df_selection.groupby("Rating").size().reset_index(name="Quantidade")
            fig_pizza = px.pie(
                df_rating,
                values="Quantidade",
                names="Rating",
                hole=0.4,
                template="plotly_dark"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

    # --- ABA DE GRÁFICOS (MENU SUPERIOR) ---
    elif st.session_state.aba_atual == "Gráficos":
        st.title("📈 Detalhamento Estatístico")

        fig_line = px.line(
            df_selection,
            x="COL 2",
            y="Investment",
            color="COL 3",
            title="Evolução de Investimentos por Localidade",
            template="plotly_dark"
        )
        st.plotly_chart(fig_line, use_container_width=True)

