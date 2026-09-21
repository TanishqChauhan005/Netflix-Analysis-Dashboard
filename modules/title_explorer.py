import pandas as pd
import streamlit as st
from src.data_loader import explode_column


def render_title_explorer(filtered_df: pd.DataFrame, raw_df: pd.DataFrame):
    st.header("🔍 Interactive Title Explorer & Recommender")

    # ------------------------------------------------------------
    # SEARCH & SCROLLABLE FILTERS (Genres, Directors, Actors)
    # ------------------------------------------------------------
    # Search Bar (Top)
    search_query = st.text_input(
        "🔎 Full-Text Search",
        placeholder="Search by title, actor, director, or keyword...",
        key="exp_search_query",
    )

    # Helper lists for scrollable Director and Actor dropdowns
    all_directors = sorted(
        filtered_df[filtered_df["director"] != "Unknown"]["director"]
        .str.split(", ")
        .explode()
        .dropna()
        .unique()
    )

    all_actors = sorted(
        filtered_df[filtered_df["cast"] != "Unknown"]["cast"]
        .str.split(", ")
        .explode()
        .dropna()
        .unique()
    )

    all_genres = sorted(explode_column(filtered_df, "listed_in")["listed_in"].unique())

    # 3-Column Scrollable Multiselect Filters
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        explorer_genres = st.multiselect(
            "🎭 Filter by Genre",
            options=all_genres,
            default=[],
            key="exp_genre_filter",
            help="Scroll or search to select genres",
        )

    with f_col2:
        explorer_directors = st.multiselect(
            "🎬 Filter by Director",
            options=all_directors,
            default=[],
            key="exp_director_filter",
            help="Scroll or search to select directors",
        )

    with f_col3:
        explorer_actors = st.multiselect(
            "🌟 Filter by Actor / Cast",
            options=all_actors,
            default=[],
            key="exp_actor_filter",
            help="Scroll or search to select actors",
        )

    # ------------------------------------------------------------
    # APPLY EXPLORER FILTERS
    # ------------------------------------------------------------
    exp_df = filtered_df.copy()

    # 1. Full-text search
    if search_query:
        query = search_query.strip()
        exp_df = exp_df[
            exp_df["title"].str.contains(query, case=False, na=False)
            | exp_df["cast"].str.contains(query, case=False, na=False)
            | exp_df["director"].str.contains(query, case=False, na=False)
            | exp_df["listed_in"].str.contains(query, case=False, na=False)
        ]

    # 2. Genre filter
    if explorer_genres:
        pattern = "|".join(explorer_genres)
        exp_df = exp_df[exp_df["listed_in"].str.contains(pattern, case=False, na=False)]

    # 3. Director filter
    if explorer_directors:
        exp_df = exp_df[
            exp_df["director"].apply(
                lambda d: any(dir_name in str(d) for dir_name in explorer_directors)
            )
        ]

    # 4. Actor filter
    if explorer_actors:
        exp_df = exp_df[
            exp_df["cast"].apply(
                lambda c: any(actor_name in str(c) for actor_name in explorer_actors)
            )
        ]

    st.markdown(f"Showing **{len(exp_df):,}** matching titles")
    st.markdown("---")

    if exp_df.empty:
        st.warning("⚠️ No matching titles found. Clear inputs to refresh.")
        return

    # ------------------------------------------------------------
    # CATALOG INDEX TABLE
    # ------------------------------------------------------------
    st.subheader("📋 Catalog Index")
    st.caption(
        "💡 *Click any row to display its focus card and recommendations below.*"
    )

    display_table_cols = ["type", "title", "release_year", "rating", "duration"]

    event = st.dataframe(
        exp_df[display_table_cols],
        use_container_width=True,
        height=380,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        key="explorer_table_selection",
    )

    selected_row_idx = event.selection.rows if event and event.selection else []
    selected_item = (
        exp_df.iloc[selected_row_idx[0]] if selected_row_idx else exp_df.iloc[0]
    )

    st.markdown("---")

    # ------------------------------------------------------------
    # FULL-WIDTH TITLE FOCUS CARD
    # ------------------------------------------------------------
    st.subheader("🎯 Title Focus Card")

    badge_color = "#E50914" if selected_item["type"] == "Movie" else "#00D26A"
    added_date_str = (
        selected_item["date_added"].strftime("%b %d, %Y")
        if pd.notna(selected_item["date_added"])
        else "N/A"
    )

    st.markdown(
        f"""
        <div style="background-color: #1f1f1f; padding: 28px; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="background-color: {badge_color}; color: white; padding: 4px 14px; border-radius: 14px; font-size: 13px; font-weight: bold;">{selected_item['type']}</span>
                <span style="color: #aaa; font-size: 14px;">Date Added: {added_date_str}</span>
            </div>
            <h1 style="margin-top: 5px; margin-bottom: 8px; color: #ffffff !important; font-size: 32px;">{selected_item['title']}</h1>
            <p style="color: #E50914; font-size: 18px; font-weight: bold; margin-bottom: 18px;">
                {selected_item['release_year']} &nbsp;•&nbsp; Rating: {selected_item['rating']} &nbsp;•&nbsp; Duration: {selected_item['duration']}
            </p>
            <p style="font-size: 15px; line-height: 1.6; color: #dddddd; margin-bottom: 20px;">
                {selected_item.get('description', 'No synopsis available for this title.')}
            </p>
            <hr style="border-color: #333; margin: 16px 0;">
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 14px;">
                <div><strong>🎭 Genres:</strong> <span style="color:#aaa">{selected_item['listed_in']}</span></div>
                <div><strong>🎬 Director:</strong> <span style="color:#aaa">{selected_item['director']}</span></div>
                <div><strong>🌟 Cast:</strong> <span style="color:#aaa">{selected_item['cast']}</span></div>
                <div><strong>🌎 Country:</strong> <span style="color:#aaa">{selected_item['country']}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------
    # RECOMMENDATIONS ENGINE (3 IN A ROW)
    # ------------------------------------------------------------
    st.subheader("🍿 More Like This")

    def find_similar_titles(target_show_id, target_genres, target_type, target_rating):
        candidates = raw_df[
            (raw_df["type"] == target_type) & (raw_df["show_id"] != target_show_id)
        ].copy()
        if candidates.empty:
            return candidates

        target_genre_set = set(target_genres.split(", "))

        def calc_score(row):
            score = 0
            row_genres = set(str(row["listed_in"]).split(", "))
            score += len(target_genre_set.intersection(row_genres)) * 3
            if row["rating"] == target_rating:
                score += 1
            return score

        candidates["similarity_score"] = candidates.apply(calc_score, axis=1)
        return candidates.sort_values(by="similarity_score", ascending=False).head(3)

    similar_df = find_similar_titles(
        selected_item["show_id"],
        str(selected_item["listed_in"]),
        selected_item["type"],
        selected_item["rating"],
    )

    if not similar_df.empty:
        rec_cols = st.columns(len(similar_df))

        for idx, (_, sim_row) in enumerate(similar_df.iterrows()):
            with rec_cols[idx]:
                st.markdown(
                    f"""
                <div style="background-color: #181818; padding: 18px; border-radius: 10px; border-top: 4px solid #E50914; min-height: 150px; height: 100%;"> <span style="font-size: 11px; color: #888; text-transform: uppercase; font-weight: bold;">{sim_row['type']}</span> <h4 style="color: #fff !important; margin-top: 4px; margin-bottom: 6px; font-size: 16px;">{sim_row['title']}</h4> <p style="color: #E50914; font-size: 12px; font-weight: bold; margin-bottom: 8px;"> {sim_row['release_year']} &nbsp;|&nbsp; {sim_row['duration']} </p> <p style="font-size: 12px; color: #aaa; margin-bottom: 0;"> <strong>Genres:</strong> {sim_row['listed_in']} </p> </div>
                """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No similar recommendations found for this title.")

    # ------------------------------------------------------------
    # EXPORT SECTION
    # ------------------------------------------------------------
    st.markdown("---")
    csv_bytes = exp_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download {len(exp_df):,} Filtered Results (CSV)",
        data=csv_bytes,
        file_name="netflix_explorer_export.csv",
        mime="text/csv",
    )
