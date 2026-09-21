# 🎬 Netflix Analytics Dashboard

An end-to-end data analytics web application and content intelligence tool built using **Streamlit**, **Plotly**, and **Pandas**. The platform delivers executive-level KPIs, deep-dive content distributions, exploratory data analysis notebooks, and an interactive title explorer with a recommendation engine.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://<your-app-url>.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

🔗 **Live Demo:** [https://netflix-analytics-dashboard-mhtjumv4funq72gwgiavb7.streamlit.app/](https://netflix-analytics-dashboard-mhtjumv4funq72gwgiavb7.streamlit.app/)

---

## 📌 Key Features

* **Executive Overview:** High-level metrics tracking total catalog size, content additions over time, Movies vs. TV Shows ratio, and global distribution.
* **Movie & TV Analysis:** Comparative analysis exploring runtime duration distributions, season counts, age rating categories, and genre evolution.
* **Title Explorer & Recommendation Engine:** Searchable and filterable catalog with similarity scoring based on genres, descriptions, and cast metadata.
* **Comprehensive EDA Notebooks:** Documented Jupyter notebooks detailing the data preprocessing pipeline, exploratory data analysis, and business insights.

---

## 🛠️ Tech Stack

* **Web Framework:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Data Visualization:** Plotly Express, Plotly Graph Objects
* **Machine Learning:** Scikit-Learn (`TfidfVectorizer`, `cosine_similarity`)
* **Analysis & Prototyping:** Jupyter Notebook

---

## 📁 Repository Structure

```text
Netflix-Analytics-Dashboard/
├── data/
│   ├── netflix_cleaned.csv            # Cleaned & preprocessed dataset
│   └── netflix_titles.csv             # Raw Kaggle Netflix catalog
├── modules/
│   ├── movie_tv_analysis.py           # Visualizations & deep-dive comparisons
│   ├── overview.py                    # Executive metrics & global trends
│   └── title_explorer.py              # Filterable catalog & recommendation engine
├── notebook/
│   ├── 01_data_preprocessing_pipeline.ipynb
│   ├── 02_netflix_eda.ipynb
│   └── 03_business_insights.ipynb
├── src/
│   └── data_loader.py                 # Data ingestion, caching & cleaning utilities
├── app.py                             # Main Streamlit application entry point
├── requirements.txt                   # Production dependencies
├── .gitignore                         # Git exclusion rules (caches, envs)
└── README.md                          # Project documentation
