# dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =============================
# Load data (CSV – deployment safe)
# =============================
@st.cache_data
def load_data():
    return pd.read_csv("data/student_predictions.csv")


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
    .stApp {
        background: radial-gradient(circle at top left, #020617 0, #020617 25%, #000000 100%);
    }
    h1,h2,h3 {color:#F9FAFB;}

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(17,24,39,1));
        border-radius:14px;
        padding:12px 16px;
        border:1px solid rgba(55,65,81,0.9);
    }

    div[data-testid="metric-container"] > div:nth-child(2) {
        color: #E5E7EB;
        font-size:1.4rem;
        font-weight:600;
    }
    </style>
    """, unsafe_allow_html=True)

    # =============================
    # Title
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
    gender_label = st.sidebar.selectbox("Gender", options=["All", "Male", "Female"])
    placement_label = st.sidebar.selectbox("Placement Status", options=["All", "Placed", "Not Placed"])

    filtered_df = df.copy()

    # Gender filter
    if gender_label != "All":
        gender_map = {"Male": 1, "Female": 0}
        filtered_df = filtered_df[filtered_df["gender"] == gender_map[gender_label]]

    # Placement filter
    if placement_label != "All":
        placement_map = {"Placed": 1, "Not Placed": 0}
        filtered_df = filtered_df[filtered_df["predicted_placement"] == placement_map[placement_label]]

    placed_df = filtered_df[filtered_df["predicted_placement"] == 1]

    # =============================
    # KPI Metrics
    # =============================
    st.subheader("📌 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Students", len(filtered_df))
    c2.metric("Placed", (filtered_df["predicted_placement"] == 1).sum())
    c3.metric("Not Placed", (filtered_df["predicted_placement"] == 0).sum())
    if not placed_df.empty:
        c4.metric("Avg Salary (LPA)", round(placed_df["predicted_salary"].mean(), 2))
    else:
        c4.metric("Avg Salary (LPA)", "N/A")

    st.divider()

    # =============================
    # Core Insights
    # =============================
    st.subheader("📊 Core Insights")
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # Placement distribution
    with row1_col1:
        fig, ax = plt.subplots()
        filtered_df["predicted_placement"].value_counts().plot(kind="bar", ax=ax, color=["#F97316","#3B82F6"])
        ax.set_xlabel("Placement (0 = No, 1 = Yes)")
        ax.set_ylabel("Count")
        ax.set_title("Placement Distribution")
        st.pyplot(fig)

    # Salary distribution
    with row1_col2:
        if not placed_df.empty:
            fig, ax = plt.subplots()
            sns.histplot(placed_df["predicted_salary"], kde=True, ax=ax, color="#60A5FA")
            ax.set_title("Salary Distribution (LPA)")
            st.pyplot(fig)
        else:
            st.info("No placed students available")

    # CGPA vs Placement
    with row2_col1:
        fig, ax = plt.subplots()
        sns.boxplot(x="predicted_placement", y="cgpa", data=filtered_df, ax=ax)
        ax.set_title("CGPA vs Placement")
        st.pyplot(fig)

    # Salary vs Experience
    with row2_col2:
        if not placed_df.empty:
            fig, ax = plt.subplots()
            sns.scatterplot(x="work_experience_months", y="predicted_salary", data=placed_df, ax=ax)
            ax.set_title("Salary vs Experience")
            st.pyplot(fig)
        else:
            st.info("No placed students available")

    st.divider()

    # =============================
    # Extra Insights Row
    # =============================
    row3_col1, row3_col2 = st.columns(2)

    # Placement rate by gender
    with row3_col1:
        st.markdown("### Placement Rate by Gender")
        if not filtered_df.empty:
            gender_stats = filtered_df.groupby("gender")["predicted_placement"].mean().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(data=gender_stats, x="gender", y="predicted_placement", ax=ax, palette=["#F97316","#3B82F6"])
            ax.set_ylabel("Placement Rate")
            ax.set_xlabel("Gender")
            ax.set_ylim(0,1)
            st.pyplot(fig)
        else:
            st.info("No data available for gender placement rate")

    # Average Salary by CGPA Band
    with row3_col2:
        st.markdown("### Avg Salary by CGPA Band")
        if not placed_df.empty:
            placed_copy = placed_df.copy()
            placed_copy["cgpa_band"] = pd.cut(
                placed_copy["cgpa"],
                bins=[0,6,7,8,9,10],
                labels=["<6","6-7","7-8","8-9","9-10"]
            )
            band_stats = placed_copy.groupby("cgpa_band")["predicted_salary"].mean().reset_index()
            fig, ax = plt.subplots()
            sns.barplot(data=band_stats, x="cgpa_band", y="predicted_salary", ax=ax, color="#60A5FA")
            ax.set_xlabel("CGPA Band")
            ax.set_ylabel("Avg Salary (LPA)")
            st.pyplot(fig)
        else:
            st.info("No placed students to calculate salary by CGPA")

    # =============================
    # Pie Chart + Correlation
    # =============================
    row4_col1, row4_col2 = st.columns(2)

    # Pie chart for placement split
    with row4_col1:
        st.markdown("### Placement Split")
        counts = filtered_df["predicted_placement"].value_counts().sort_index()
        labels = ["Not Placed","Placed"]
        sizes = [counts.get(0,0), counts.get(1,0)]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, colors=["#F97316","#22C55E"])
        ax.axis("equal")
        st.pyplot(fig)

    # Correlation heatmap
    with row4_col2:
        st.markdown("### Feature Correlation")
        numeric_cols = ["cgpa","attendance_percentage","technical_skill_score",
                        "soft_skill_score","work_experience_months","predicted_salary","predicted_placement"]
        available_cols = [c for c in numeric_cols if c in filtered_df.columns]
        if len(available_cols) >= 2:
            corr = filtered_df[available_cols].corr()
            fig, ax = plt.subplots(figsize=(5,4))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.info("Not enough numeric columns for correlation heatmap")

    # =============================
    # Deep Dive Tabs
    # =============================
    st.subheader("📈 Deep Dive Analysis")
    tab1, tab2, tab3 = st.tabs(["Skills","Academics","Raw Data"])

    with tab1:
        fig, ax = plt.subplots()
        sns.scatterplot(
            x="technical_skill_score",
            y="soft_skill_score",
            hue="predicted_placement",
            data=filtered_df,
            ax=ax
        )
        ax.set_title("Technical vs Soft Skills")
        st.pyplot(fig)

    with tab2:
        fig, ax = plt.subplots()
        sns.boxplot(
            x="predicted_placement",
            y="attendance_percentage",
            data=filtered_df,
            ax=ax
        )
        ax.set_title("Attendance vs Placement")
        st.pyplot(fig)

    with tab3:
        st.dataframe(filtered_df, use_container_width=True)
