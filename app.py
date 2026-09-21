import streamlit as st
from modules.movie_tv_analysis import render_movie_tv_analysis
from modules.overview import render_overview
from modules.title_explorer import render_title_explorer
from src.data_loader import load_data

st.set_page_config(
    page_title="Netflix",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(
                circle at 50% 0%,
                #201111 0%,
                #111111 50%,
                #0a0a0a 100%
            ) !important;
            background-attachment: fixed !important;
            color: #FFFFFF;
        }

        section[data-testid="stSidebar"] {
            background-color: #0d0d0d !important;
            border-right: 1px solid #222222;
        }

        h1,
        h2,
        h3 {
            color: #E50914 !important;
            font-family: 'Helvetica Neue',
            Helvetica,
            Arial,
            sans-serif;
        }

        div[data-testid="stMetric"] {
            background: rgba(30, 30, 30, 0.65) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(229, 9, 20, 0.25) !important;
            padding: 18px;
            border-radius: 12px;
            box-shadow:
                0 8px 16px rgba(0, 0, 0, 0.5),
                0 0 12px rgba(229, 9, 20, 0.15);
            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow:
                0 12px 20px rgba(0, 0, 0, 0.7),
                0 0 20px rgba(229, 9, 20, 0.3);
            border: 1px solid rgba(229, 9, 20, 0.5) !important;
        }

        div[data-testid="stMetricLabel"] > label {
            color: #b3b3b3 !important;
            font-size: 14px !important;
        }

        div[data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-weight: 800;
            font-size: 32px !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #1a1a1a;
            border-radius: 6px 6px 0px 0px;
            padding: 10px 22px;
            color: #b3b3b3;
            border: 1px solid #2a2a2a;
        }

        .stTabs [aria-selected="true"] {
            background-color: #E50914 !important;
            color: #ffffff !important;
            font-weight: bold;
            border: 1px solid #E50914 !important;
        }

        hr {
            border: none;
            height: 1px;
            background: linear-gradient(
                to right,
                #E50914,
                rgba(229, 9, 20, 0.1)
            );
            margin: 25px 0;
        }

        .header-container {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 5px;
        }

        .header-logo {
            height: 48px;
            width: auto;
            filter: drop-shadow(
                0px 0px 8px rgba(229, 9, 20, 0.4)
            );
        }

        .header-title {
            color: #E50914;
            font-size: 36px;
            font-weight: 800;
            margin: 0;
            padding: 0;
            font-family: 'Helvetica Neue',
            Helvetica,
            Arial,
            sans-serif;
        }

        .main h1 {
            font-size: 42px !important;
        }

        .main h2 {
            font-size: 30px !important;
        }

        .main h3 {
            font-size: 22px !important;
        }

        .main p,
        .main span,
        .main label {
            font-size: 16px !important;
        }

        .main div[data-testid="stMetricValue"] > div {
            font-size: 32px !important;
        }

        .main div[data-testid="stMetricLabel"] > label {
            font-size: 14px !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            font-size: 18px !important;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            font-size: 13px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stMetricValue"] > div {
            font-size: 20px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stMetricLabel"] > label {
            font-size: 12px !important;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# Load Data
st.sidebar.title("🎬 Netflix Analytics")
st.sidebar.caption("v2.5 Platform Dashboard")
st.sidebar.markdown("---")

st.session_state.setdefault("uploaded_dataset", None)

try:
    if st.session_state.uploaded_dataset:
        df = load_data(st.session_state.uploaded_dataset)
    else:
        try:
            df = load_data("data/netflix_titles.csv")
        except FileNotFoundError:
            df = load_data("netflix_titles.csv")
except Exception as e:
    st.error(f"❌ Error loading dataset: {e}")
    st.stop()

# Sidebar Filters
st.sidebar.header("🔎 Global Filters")
all_types = sorted(df["type"].dropna().unique())
content_types = st.sidebar.multiselect(
    "Content Type",
    options=all_types,
    default=all_types,
    help="Filter between Movies and TV Shows",
)

min_year = int(df["release_year"].min()) if not df.empty else 1920
max_year = int(df["release_year"].max()) if not df.empty else 2021
release_year_range = st.sidebar.slider(
    "Release Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    help="Select the release time span",
)

filtered_df = df[
    df["type"].isin(content_types)
    & df["release_year"].between(release_year_range[0], release_year_range[1])
].copy()

# Sidebar Stats
st.sidebar.markdown("---")
st.sidebar.header("📊 Dataset Health & Quick Stats")

s_col1, s_col2 = st.sidebar.columns(2)
s_col1.metric("Total Titles", f"{len(filtered_df):,}")
s_col2.metric("Movies", f"{(filtered_df['type'] == 'Movie').sum():,}")

s_col3, s_col4 = st.sidebar.columns(2)
s_col3.metric("TV Shows", f"{(filtered_df['type'] == 'TV Show').sum():,}")
s_col4.metric("Span", f"{release_year_range[0]}-{release_year_range[1]}")

# Sidebar File Uploader
st.sidebar.markdown("---")
st.sidebar.header("📁 Load Custom Dataset")
uploaded_file = st.sidebar.file_uploader(
    "Upload custom `netflix_titles.csv`",
    type=["csv"],
    help="Upload an updated or custom Netflix dataset CSV file.",
)

if uploaded_file and uploaded_file != st.session_state.uploaded_dataset:
    st.session_state.uploaded_dataset = uploaded_file
    st.rerun()

# Main Header & Body
st.markdown(
    """<div class="header-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" class="header-logo" alt="Netflix Logo">
        <h1 class="header-title"></h1>
    </div>""",
    unsafe_allow_html=True,
)
st.caption(
    "Interactive intelligence platform summarizing catalog macro trends, content distributions, and detailed title exploration."
)
st.markdown("---")

# Navigation Tabs
tab_overview, tab_movie_tv, tab_explorer = st.tabs(
    ["🏠 Overview", "🎬 Movie & TV Analysis", "🔍 Title Explorer"]
)

with tab_overview:
    render_overview(filtered_df)
with tab_movie_tv:
    render_movie_tv_analysis(filtered_df)
with tab_explorer:
    render_title_explorer(filtered_df, df)

st.markdown("---")
st.caption("Netflix Analytics Platform | Built with Python, Pandas, Plotly & Streamlit")
