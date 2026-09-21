import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import explode_column


def render_movie_tv_analysis(filtered_df: pd.DataFrame):
    st.header("🎬 Movie & TV Analysis")
    st.caption(
        "Key performance metrics, catalog genres, target audience composition, movie lengths, season breakdowns, and director analytics."
    )

    if filtered_df.empty:
        st.warning("⚠️ No data available for the currently selected global filters.")
        return

    # ------------------------------------------------------------
    # KPI METRIC CARDS
    # ------------------------------------------------------------
    total_movies = (filtered_df["type"] == "Movie").sum()
    total_tv = (filtered_df["type"] == "TV Show").sum()

    avg_movie_duration = filtered_df.loc[
        filtered_df["type"] == "Movie", "duration_minutes"
    ].mean()

    # Find top genre
    genre_df = explode_column(filtered_df, "listed_in")
    top_genre_series = genre_df["listed_in"].value_counts()
    top_genre = top_genre_series.index[0] if not top_genre_series.empty else "N/A"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Movies", f"{total_movies:,}")
    k2.metric("Total TV Shows", f"{total_tv:,}")
    k3.metric(
        "Avg Movie Length",
        "N/A" if pd.isna(avg_movie_duration) else f"{avg_movie_duration:.1f} min",
    )
    k4.metric("Top Genre", top_genre)

    st.markdown("---")

    # ------------------------------------------------------------
    # ROW 1: GENRES & TARGET AUDIENCE
    # ------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        top_genres = (
            top_genre_series
            .head(10)
            .sort_values(ascending=True)
            .reset_index(name="count")
        )

        fig_genre = px.bar(
            top_genres,
            x="count",
            y="listed_in",
            orientation="h",
            title="Top 10 Genres",
            color_discrete_sequence=["#E50914"],
        )
        fig_genre.update_layout(
            template="plotly_dark",
            yaxis_title=None,
            margin=dict(t=40, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_genre, use_container_width=True)

    with col2:
        mat_counts = (
            filtered_df["maturity_bucket"]
            .value_counts()
            .reset_index(name="count")
        )
        fig_mat = px.pie(
            mat_counts,
            names="maturity_bucket",
            values="count",
            hole=0.4,
            title="Target Audience Composition",
            color_discrete_sequence=["#E50914", "#B81D24", "#221F1F", "#666666"],
        )
        fig_mat.update_layout(
            template="plotly_dark", margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_mat, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------
    # ROW 2: MOVIE DURATIONS & TV SEASONS
    # ------------------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        m_dur = filtered_df[
            (filtered_df["type"] == "Movie")
            & (filtered_df["duration_minutes"].notna())
        ]
        if not m_dur.empty:
            fig_dur = px.histogram(
                m_dur,
                x="duration_minutes",
                nbins=25,
                marginal="box",
                title="Movie Duration Spread",
                color_discrete_sequence=["#E50914"],
            )
            fig_dur.update_layout(
                template="plotly_dark",
                xaxis_title="Minutes",
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_dur, use_container_width=True)
        else:
            st.info("No Movies available for current global filters.")

    with col4:
        tv_seas = filtered_df[
            (filtered_df["type"] == "TV Show") & (filtered_df["seasons"].notna())
        ]
        if not tv_seas.empty:
            seas_counts = (
                tv_seas["seasons"]
                .value_counts()
                .sort_index()
                .reset_index(name="count")
            )
            fig_seas = px.bar(
                seas_counts,
                x="seasons",
                y="count",
                title="TV Show Season Breakdown",
                color_discrete_sequence=["#E50914"],
            )
            fig_seas.update_layout(
                template="plotly_dark",
                xaxis_title="Seasons",
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_seas, use_container_width=True)
        else:
            st.info("No TV Shows available for current global filters.")

    st.markdown("---")

    # ------------------------------------------------------------
    # ROW 3: TOP DIRECTORS LEADERBOARD
    # ------------------------------------------------------------
    st.subheader("🎬 Top Directors Leaderboard")

    exploded_directors = (
        filtered_df[filtered_df["director"] != "Unknown"][["show_id", "director"]]
        .assign(director=lambda x: x["director"].str.split(", "))
        .explode("director")
    )

    directors_df = (
        exploded_directors["director"]
        .value_counts()
        .head(10)
        .reset_index(name="Total Titles")
    )
    directors_df.columns = ["Director", "Total Titles"]

    st.dataframe(
        directors_df,
        column_config={
            "Director": "Director Name",
            "Total Titles": st.column_config.NumberColumn(
                "Total Titles", format="%d"
            ),
        },
        use_container_width=True,
        hide_index=True,
    )