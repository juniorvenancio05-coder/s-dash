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
tema_azul_escuro_topo = """
  # 1. BLOCO DE CONFIGURAÇÃO VISUAL (Apenas CSS válido)
st.markdown("""
import streamlit as st

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
# FIM DO BLOCO DE CSS

# Imagem centralizada fora do CSS apontando para a pasta data
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("data/logo1.webp", width=150)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(tema_azul_escuro_topo, unsafe_allow_html=True)

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
    # Renderização da aba principal (Métricas + Tabela)
    total1, total2, total3, total4, total5 = st.columns(5)

    with total1:
        st.metric(label="📊 Total Investment", value=f"{total_investment:,.0f}")
    with total2:
        st.metric(label="🔝 Most Frequent", value=f"{investment_mode:,.0f}")
    with total3:
        st.metric(label="📈 Average", value=f"{investment_mean:,.0f}")
    with total4:
        st.metric(label="🎯 Central Earnings", value=f"{investment_median:,.0f}")
    with total5:
        st.metric(label="⭐ Rating Total", value=numerize(rating_sum), help=f"Total: {rating_sum}")

    st.markdown("##")

    with st.expander("Tabular View", expanded=True):
        showData = st.multiselect('Filter Columns:', options=list(df_selection.columns))
        df_to_show = df_selection[showData] if showData else df_selection

        if not df_to_show.empty:
            if "Investment" in df_to_show.columns:
                styled_df = df_to_show.style.background_gradient(cmap="Blues", subset=["Investment"])
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.dataframe(df_to_show, use_container_width=True)

elif st.session_state.aba_atual == "Gráficos":
    # Renderização da aba de gráficos
    investment_by_business_type = df_selection.groupby(by=["BusinessType"], as_index=False)[
        "Investment"].sum().sort_values(by="Investment", ascending=True)
    fig_investment = px.bar(
        investment_by_business_type, x="Investment", y="BusinessType", orientation="h",
        title="<b>Investment by Business Type</b>", color_discrete_sequence=["#154c79"], template="plotly_dark"
    )

    investment_by_state = df_selection.groupby(by=["COL 2"], as_index=False)["Investment"].sum().sort_values(
        by="Investment", ascending=True)
    fig_state = px.bar(
        investment_by_state, x="Investment", y="COL 2", orientation="h",
        title="<b>Investment by Location</b>", color_discrete_sequence=["#154c79"], template="plotly_dark"
    )

    for fig in [fig_investment, fig_state]:
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="#001122", font_color="#ffffff",
                          margin=dict(l=20, r=20, t=40, b=20))

    col_grafico1, col_grafico2 = st.columns(2)
    with col_grafico1:
        st.plotly_chart(fig_investment, use_container_width=True)
    with col_grafico2:
        st.plotly_chart(fig_state, use_container_width=True)


# --- FUNÇÃO DA VISUALIZAÇÃO TABULAR COLORIDA ---
def Home():
    with st.expander("Tabular View"):
        showData = st.multiselect('Filter Columns:', options=list(df_selection.columns),
                                  key='multiselect_filter_columns_unique')

        df_to_show = df_selection[showData] if showData else df_selection

        if not df_to_show.empty:
            if "Investment" in df_to_show.columns:
                # Gradiente de cor azul escuro que combina com o tema da página
                styled_df = df_to_show.style.background_gradient(cmap="Blues", subset=["Investment"])
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.dataframe(df_to_show, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir.")


# --- FUNÇÃO DOS GRÁFICOS COMPATÍVEIS ---
def graphs():
    if not df_selection.empty:
        investment_by_business_type = df_selection.groupby(by=["BusinessType"], as_index=False)["Investment"].sum()
        investment_by_business_type = investment_by_business_type.sort_values(by="Investment", ascending=True)

        fig_investment = px.bar(
            investment_by_business_type,
            x="Investment",
            y="BusinessType",
            orientation="h",
            title="<b>Investment by Business Type</b>",
            color_discrete_sequence=["#154c79"],
            template="plotly_dark",  # Força os gráficos a usarem fundo escuro
        )

        investment_by_state = df_selection.groupby(by=["COL 2"], as_index=False)["Investment"].sum()
        investment_by_state = investment_by_state.sort_values(by="Investment", ascending=True)

        fig_state = px.bar(
            investment_by_state,
            x="Investment",
            y="COL 2",
            orientation="h",
            title="<b>Investment by Location</b>",
            color_discrete_sequence=["#154c79"],
            template="plotly_dark",  # Força os gráficos a usarem fundo escuro
        )

        # Remove fundos cinzas do Plotly para fundir perfeitamente com o fundo azul escuro do app
        # Adicione essas atualizações de layout logo após criar fig_state e fig_investment:
        fig_state.update_layout(
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20),  # Reduz as margens laterais no celular
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#2e374a"),
            yaxis=dict(showgrid=False)
        )

        fig_investment.update_layout(
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#2e374a"),
            yaxis=dict(showgrid=False)
        )

        left, right = st.columns(2)
        left.plotly_chart(fig_investment, use_container_width=True)
        right.plotly_chart(fig_state, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para gerar gráficos.")


# --- FUNÇÃO DA BARRA DE PROGRESSO ---
def Progressbar():
    st.subheader("🎯 Metas de Investimento")

    target = 30000000
    current = df_selection["Investment"].sum()

    percent = int(round((current / target * 100))) if target > 0 else 0
    percent_capped = min(percent, 100)

    mybar = st.progress(0)

    if percent >= 100:
        st.success(f"Target Done! Você atingiu {percent}% da meta acumulada.")
    else:
        st.write(f"Você completou **{percent}%** do objetivo de **{target:,} TZS**.")

    for percent_complete in range(percent_capped):
        time.sleep(0.01)
        mybar.progress(percent_complete + 1, text="Progresso da Meta")


# --- MENU DE NAVEGAÇÃO LATERAL (CONTROLADOR ESPATIAL) ---
def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Progress"],
            icons=["house", "eye"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"background-color": "#0c1929"},
                "icon": {"color": "#154c79", "font-size": "18px"},
                "nav-link": {"color": "#ffffff"},
                "nav-link-selected": {"background-color": "#154c79", "color": "white"},
            }
        )

    if selected == "Home":
        Home()
        graphs()
    elif selected == "Progress":
        Progressbar()


# Executa o menu e o painel correspondente
sideBar()
