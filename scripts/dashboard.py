# dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from db_connection import load_data  # make sure db_connection.py has load_data()

def run_dashboard():
    # =============================
    # Page config
    # =============================
    st.set_page_config(
        page_title="Student Placement Dashboard",
        layout="wide"
    )

    # =============================
    # Global plot theme (dark)
    # =============================
    plt.style.use("dark_background")
    sns.set_style("darkgrid")

    # =============================
    # Custom CSS
    # =============================
    st.markdown("""
    <style>
    /* App background */
    .stApp {background: radial-gradient(circle at top left, #020617 0, #020617 25%, #000000 100%);}
    h1,h2,h3 {color:#F9FAFB;}
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(17,24,39,1));
        border-radius:14px; padding:12px 16px;
        border:1px solid rgba(55,65,81,0.9);
    }
    div[data-testid="metric-container"] > div:nth-child(2) {
        color: #E5E7EB; font-size:1.4rem; font-weight:600;
    }
    .chart-card {
        background: radial-gradient(circle at top left, #020617 0, #020617 45%, #020617 100%);
        border-radius:18px; padding:16px;
        border:1px solid rgba(55,65,81,0.9);
    }
    </style>
    """, unsafe_allow_html=True)

    # =============================
# Title + Hero Summary
# =============================
    st.title("🎓 Student Placement & Salary Prediction Dashboard")



    # =============================
    # Load data
    # =============================
    df = load_data()

    # =============================
    # Sidebar filters
    # =============================
    st.sidebar.header("🔍 Filters")

    gender_label = st.sidebar.selectbox(
        "Gender",
        options=["All", "Male", "Female"]
    )

    placement_label = st.sidebar.selectbox(
        "Placement Status",
        options=["All", "Placed", "Not Placed"]
    )

    filtered_df = df.copy()

    # Map labels -> codes
    if gender_label != "All":
        gender_map = {"Male":1, "Female":0}  # adjust if needed
        filtered_df = filtered_df[filtered_df["gender"] == gender_map[gender_label]]

    if placement_label != "All":
        placement_map = {"Placed":1, "Not Placed":0}
        filtered_df = filtered_df[filtered_df["predicted_placement"] == placement_map[placement_label]]

    placed_df = filtered_df[filtered_df["predicted_placement"]==1]

    # =============================
    # KPI Metrics
    # =============================
    st.subheader("📌 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", len(filtered_df))
    c2.metric("Placed", (filtered_df["predicted_placement"]==1).sum())
    c3.metric("Not Placed", (filtered_df["predicted_placement"]==0).sum())
    if not placed_df.empty:
        c4.metric("Avg Salary (LPA)", round(placed_df["predicted_salary"].mean(),2))
    else:
        c4.metric("Avg Salary (LPA)", "N/A")

    st.divider()

    # =============================
    # Core Charts
    # =============================
    st.subheader("📊 Core Insights")
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # Placement distribution
    with row1_col1:
        fig, ax = plt.subplots()
        filtered_df["predicted_placement"].value_counts().plot(kind="bar", ax=ax, color=["#F97316","#3B82F6"])
        ax.set_xlabel("Placement (0=No,1=Yes)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    # Salary distribution
    with row1_col2:
        if not placed_df.empty:
            fig, ax = plt.subplots()
            sns.histplot(placed_df["predicted_salary"], kde=True, ax=ax, color="#60A5FA")
            ax.set_xlabel("Salary (LPA)")
            st.pyplot(fig)
        else:
            st.info("No placed students for salary distribution")

    # CGPA vs Placement
    with row2_col1:
        fig, ax = plt.subplots()
        sns.boxplot(x="predicted_placement", y="cgpa", data=filtered_df, ax=ax)
        st.pyplot(fig)

    # Salary vs Experience
    with row2_col2:
        if not placed_df.empty:
            fig, ax = plt.subplots()
            sns.scatterplot(x="work_experience_months", y="predicted_salary", data=placed_df, ax=ax)
            st.pyplot(fig)
        else:
            st.info("No placed students for experience vs salary")

    st.divider()

    # =============================
    # Deep Dive Tabs
    # =============================
    st.subheader("📈 Deep Dive Analysis")
    tab1, tab2, tab3 = st.tabs(["Skills","Academics","Raw Data"])

    # Skills
    with tab1:
        fig, ax = plt.subplots()
        sns.scatterplot(x="technical_skill_score", y="soft_skill_score",
                        hue="predicted_placement", data=filtered_df, ax=ax)
        st.pyplot(fig)

    # Academics
    with tab2:
        fig, ax = plt.subplots()
        sns.boxplot(x="predicted_placement", y="attendance_percentage", data=filtered_df, ax=ax)
        st.pyplot(fig)

    # Raw Data
    with tab3:
        st.dataframe(filtered_df, use_container_width=True)
