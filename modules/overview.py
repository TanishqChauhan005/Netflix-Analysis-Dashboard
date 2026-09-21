import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import explode_column


def render_overview(filtered_df: pd.DataFrame):
    st.header("🏠 Executive Overview")
    st.caption(
        "Macro overview of Netflix catalog growth, distribution ratios, release trends, and international production hubs."
    )

    if filtered_df.empty:
        st.warning("⚠️ No data available for the currently selected global filters.")
        return


    #                   KPI CARDS
    total_titles = filtered_df["show_id"].nunique()
    total_movies = (filtered_df["type"] == "Movie").sum()
    total_tv = (filtered_df["type"] == "TV Show").sum()
    avg_movie_duration = filtered_df.loc[
        filtered_df["type"] == "Movie", "duration_minutes"
    ].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Titles", f"{total_titles:,}")
    k2.metric("Movies", f"{total_movies:,}")
    k3.metric("TV Shows", f"{total_tv:,}")
    k4.metric(
        "Avg Movie Duration",
        "N/A" if pd.isna(avg_movie_duration) else f"{avg_movie_duration:.1f} min",
    )

    st.markdown("---")


    #               ROW 1: SPLIT & CONTENT GROWTH
    col1, col2 = st.columns(2)

    with col1:
        type_counts = filtered_df["type"].value_counts().reset_index(name="count")
        fig_type = px.pie(
            type_counts,
            names = "type",
            values = "count",
            hole = 0.55,
            title = "Movies vs TV Shows Ratio",
            color_discrete_sequence=["#E50914", "#221F1F"],
        )
        fig_type.update_layout(
            template = "plotly_dark",
            margin = dict(t=40, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        content_year = (
            filtered_df.dropna(subset = ["added_year"])
            .groupby(["added_year", "type"])
            .size()
            .reset_index(name = "count")
        )

        fig_year = px.line(
            content_year,
            x = "added_year",
            y = "count",
            color = "type",
            markers = True,
            title = "Catalog Additions Over Time",
            color_discrete_map = {"Movie": "#E50914", "TV Show": "#00D26A"},
        )
        fig_year.update_layout(
            template = "plotly_dark",
            xaxis_title = "Year Added",
            yaxis_title = "Titles Added",
            margin = dict(t=40, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_year, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------
    # ROW 2: RELEASE YEAR TRENDS & CATALOG AGE GAP
    # ------------------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        release_counts = (
            filtered_df["release_year"]
            .value_counts()
            .head(10)
            .sort_index()
            .reset_index(name="count")
        )

        fig_release = px.bar(
            release_counts,
            x = "release_year",
            y = "count",
            title = "Top Content Output Years (Release Year)",
            color_discrete_sequence = ["#E50914"],
        )
        fig_release.update_layout(
            template = "plotly_dark",
            xaxis_title = "Release Year",
            yaxis_title = "Number of Titles",
            margin = dict(t=40, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_release, use_container_width=True)

    with col4:
        valid_years_df = filtered_df.dropna(subset = ["added_year", "release_year"])

        fig_scatter = px.scatter(
            valid_years_df,
            x = "release_year",
            y = "added_year",
            color = "type",
            opacity = 0.6,
            title = "Release Year vs. Year Added to Netflix",
            color_discrete_map = {"Movie": "#E50914", "TV Show": "#00D26A"},
            hover_data = ["title"],
        )
        fig_scatter.update_layout(
            template = "plotly_dark",
            xaxis_title = "Original Release Year",
            yaxis_title = "Year Added to Netflix",
            margin = dict(t=40, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------
    # ROW 3: GLOBAL PRODUCTION HUBS
    # ------------------------------------------------------------
    exploded_country = explode_column(filtered_df, "country")
    top_c = (
        exploded_country["country"]
        .value_counts()
        .head(10)
        .sort_values(ascending=True)
        .reset_index(name="count")
    )

    fig_top_c = px.bar(
        top_c,
        x = "count",
        y = "country",
        orientation = "h",
        color_discrete_sequence = ["#E50914"],
        title = "Top 10 Global Content-Producing Countries",
    )
    fig_top_c.update_layout(
        template = "plotly_dark",
        xaxis_title = "Titles Count",
        yaxis_title = None,
        margin = dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_top_c, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------
    # ROW 4: TOP COUNTRY PRODUCTION SUMMARY TABLE
    # ------------------------------------------------------------
    st.subheader("📊 Top Country Production Summary")

    top_countries_list = top_c["country"].tolist()
    country_summary_df = (
        exploded_country[exploded_country["country"].isin(top_countries_list)]
        .groupby(["country", "type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    if "Movie" not in country_summary_df.columns:
        country_summary_df["Movie"] = 0
    if "TV Show" not in country_summary_df.columns:
        country_summary_df["TV Show"] = 0

    country_summary_df["Total Titles"] = (
        country_summary_df["Movie"] + country_summary_df["TV Show"]
    )
    country_summary_df["Movie Share (%)"] = (
        (country_summary_df["Movie"] / country_summary_df["Total Titles"]) * 100
    ).round(1)

    country_summary_df = country_summary_df.sort_values(
        by="Total Titles", ascending=False
    )

    st.dataframe(
        country_summary_df,
        column_order=["country", "Total Titles", "Movie", "TV Show", "Movie Share (%)"],
        column_config={
            "country": "Country",
            "Total Titles": st.column_config.NumberColumn("Total Titles"),
            "Movie": st.column_config.NumberColumn("Movies"),
            "TV Show": st.column_config.NumberColumn("TV Shows"),
            "Movie Share (%)": st.column_config.ProgressColumn(
                "Movie Ratio (%)", format="%.1f%%", min_value=0, max_value=100
            ),
        },
        use_container_width=True,
        hide_index=True,
    )
