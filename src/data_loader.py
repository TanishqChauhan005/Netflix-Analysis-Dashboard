import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def load_data(file_path: str = "data/netflix_titles.csv") -> pd.DataFrame:

    df = pd.read_csv(file_path)

    #                   Data Cleaning
    # Clean title whitespace
    df['title'] = df['title'].fillna("Unknown")

    # Clean date strings safely
    df['date_added'] = df['date_added'].astype(str).str.strip()
    df['date_added'] = pd.to_datetime(
        df['date_added'], errors="coerce"
    )

    # Fill missing text attributes
    text_columns = ['director', 'cast', 'country', 'rating', 'duration']
    for col in text_columns:
        df[col] = df[col].fillna("Unknown")



    #                   Feature Engineering
    # Extract year, month number, and month name from the 'date_added' column
    df['added_year'] = df['date_added'].dt.year
    df['added_month'] = df['date_added'].dt.month
    df['added_month_name'] = df['date_added'].dt.month_name()

    # Extract Numerical duration values
    df['duration_value'] = pd.to_numeric(
        df['duration'].str.extract(r"(\d+)")[0], errors="coerce"
    )

    # Separate movie duration (minutes) and TV duration (seasons)
    df["duration_minutes"] = np.where(
        df["type"] == "Movie", df["duration_value"], np.nan
    )

    df["seasons"] = np.where(
        df["type"] == "TV Show", df["duration_value"], np.nan
    )

    # Calculate content age when added to Netflix
    df["content_age"] = df["added_year"] - df["release_year"]

    # Audience Maturity Buckets
    rating_map = {
        "G": "Kids & Family",
        "PG": "Kids & Family",
        "TV-Y": "Kids & Family",
        "TV-Y7": "Kids & Family",
        "TV-Y7-FV": "Kids & Family",
        "TV-G": "Kids & Family",
        "PG-13": "Teens / YA",
        "TV-14": "Teens / YA",
        "R": "Mature / Adult",
        "NC-17": "Mature / Adult",
        "TV-MA": "Mature / Adult",
        "UR": "Unrated",
        "NR": "Unrated",
        "Unknown": "Unrated",
    }
    df["maturity_bucket"] = df["rating"].map(rating_map).fillna("Unrated")

    return df

       

def explode_column(dataframe: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Helper to explode multi-value comma-separated columns (e.g., country, listed_in)."""
    return (
        dataframe[dataframe[col_name] != "Unknown"][["show_id", "type", col_name]]
        .assign(**{col_name: lambda x: x[col_name].str.split(", ")})
        .explode(col_name)
    )