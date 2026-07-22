import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
from query import *
import os
import time

# Configuração da página (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded" # Força a abertura do menu lateral
)

# --- FORÇAR TEMA AZUL ESCURO DIRETAMENTE VIA PYTHON (CSS) ---
tema_azul_escuro_mobile = """
    <style>
    /* Ocultar menus padrões do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fundo geral da página */
    .stApp {
        background-color: #001122 !important;
        color: #ffffff !important;
    }

    /* Cores de texto globais */
    h1, h2, h3, h4, h5, h6, p, label, .stSubheader {
        color: #ffffff !important;
    }

    /* Barra lateral visível no mobile */
    section[data-testid="stSidebar"] {
        background-color: #0c1929 !important;
        border-right: 1px solid #154c79 !important;
    }

    /* Caixas de Métricas Responsivas */
    div[data-testid="stMetricSimpleContainer"], div[data-testid="stMetricContainer"] {
        background-color: #0c1929 !important;
        border: 1px solid #154c79 !important;
        padding: 12px !important; /* Menor padding para telas pequenas */
        border-radius: 10px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
        margin-bottom: 10px !important; /* Espaço quando empilhar no mobile */
    }

    /* Ajuste de tamanho de fonte para métricas no celular */
    div[data-testid="stMetricLabel"] > div {
        color: #ffffff !important;
        font-size: 0.9rem !important; /* Fonte ligeiramente menor */
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.5rem !important; /* Fonte menor para não quebrar linha */
    }

    /* Notificações responsivas */
    div[data-testid="stNotification"] {
        background-color: #154c79 !important;
        color: #ffffff !important;
        border-left: 5px solid #4a90e2 !important;
    }
    div[data-testid="stNotification"] p {
        color: #ffffff !important;
    }

    /* Media query para ajustes finos em telas menores que 768px (Celulares) */
    @media (max-width: 768px) {
        .stApp {
            padding: 10px !important;
        }
        /* Força as colunas a terem um espaçamento limpo ao empilhar */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    </style>
"""
st.markdown(tema_azul_escuro_mobile, unsafe_allow_html=True)

st.subheader("Insurance Descriptive Analytics")
st.markdown("##")

## 1. Buscar dados e criar o DataFrame base
result = view_all_data()
df = pd.DataFrame(result, columns=["COL 1", "COL 2", "COL 3", "Investment", "Rating", "BusinessType"])

# --- BARRA LATERAL ---
# Exibir logotipo com tratamento de erro
if os.path.exists("data/logo1.webp"):
    st.sidebar.image("data/logo1.webp", caption="Online Analytics")
else:
    st.sidebar.warning("Logo não encontrada")

st.sidebar.header("Por favor, filtre:")

# FILTRO 1: Região (Filtro Pai)
region = st.sidebar.selectbox(
    "Selecione a Região",
    options=df["COL 1"].unique()
)

# FILTRAGEM INTERMEDIÁRIA: Cria um dataframe temporário apenas com a região selecionada
# Isso garante que o celular não trave e nem limpe os dados por filtros conflitantes
df_filtrado_por_regiao = df[df["COL 1"] == region]

# FILTRO 2: Localização (Baseado apenas na região escolhida)
opcoes_localizacao = df_filtrado_por_regiao["COL 2"].unique()
location = st.sidebar.multiselect(
    "Select Location",
    options=opcoes_localizacao,
    default=opcoes_localizacao, # Agora o padrão são apenas as cidades daquela região
)

# FILTRO 3: Construção (Baseado na região e nas cidades selecionadas)
df_filtrado_por_local = df_filtrado_por_regiao[df_filtrado_por_regiao["COL 2"].isin(location)]
opcoes_construcao = df_filtrado_por_local["COL 3"].unique()

construction = st.sidebar.multiselect(
    "Select Construction",
    options=opcoes_construcao,
    default=opcoes_construcao, # Agora o padrão se adapta dinamicamente
)

# 2. Aplicação final e segura dos filtros para gerar o DataFrame do Dashboard
df_selection = df_filtrado_por_local[df_filtrado_por_local["COL 3"].isin(construction)]

# --- PROTEÇÃO CONTRA CONTEÚDO VAZIO ---
# Se o filtro resultar em nada, avisa o usuário em vez de quebrar a tela do celular
if df_selection.empty:
    st.warning("⚠️ Nenhum dado encontrado para a combinação de filtros selecionada.")
else:
    # Coloque aqui os seus blocos de st.metric, st.plotly_chart, etc.
    # Exemplo:
    st.success(f"Dados carregados com sucesso! Linhas disponíveis: {len(df_selection)}")

# --- CÁLCULO DAS MÉTRICAS ---
df_selection["Investment"] = pd.to_numeric(df_selection["Investment"], errors='coerce').fillna(0)
df_selection["Rating"] = pd.to_numeric(df_selection["Rating"], errors='coerce').fillna(0)

total_investment = float(df_selection["Investment"].sum())

mode_series = df_selection["Investment"].mode()
investment_mode = float(mode_series.iloc[0]) if not mode_series.empty else 0.0

investment_mean = float(df_selection["Investment"].mean()) if not df_selection.empty else 0.0
investment_median = float(df_selection["Investment"].median()) if not df_selection.empty else 0.0
rating_sum = float(df_selection["Rating"].sum())

# Exibição das Métricas em Colunas Globais
total1, total2, total3, total4, total5 = st.columns([1, 1, 1, 1, 1])

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

st.markdown("""___""")


# --- FUNÇÃO DA VISUALIZAÇÃO TABULAR COLORIDA ---
def Home():
    with st.expander("Tabular View"):
        showData = st.multiselect('Filter Columns:', options=list(df_selection.columns))
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
