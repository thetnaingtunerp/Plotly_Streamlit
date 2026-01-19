import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Descriptive Statistics Dashboard",
    layout="wide"
)

st.title("📊 Descriptive Statistics Dashboard")

# ----------------------------
# Sample Dataset
# ----------------------------
np.random.seed(42)

df = pd.DataFrame({
    "Age": np.random.randint(20, 60, 200),
    "Salary": np.random.randint(2000, 10000, 200),
    "Experience": np.random.randint(1, 35, 200)
})

st.subheader("📄 Sample Dataset")
st.dataframe(df.head(10), use_container_width=True)

# ----------------------------
# Sidebar Controls
# ----------------------------
st.sidebar.header("⚙️ Controls")
column = st.sidebar.selectbox(
    "Select Column",
    df.select_dtypes(include=np.number).columns
)

# ----------------------------
# KPI Metrics
# ----------------------------
st.markdown("""
<style>
.kpi-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    text-align: center;
}
.kpi-title {
    font-size: 14px;
    color: #6c757d;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #212529;
}
.kpi-delta {
    font-size: 13px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

def kpi_card(title, value, delta=None, emoji="📊"):
    delta_html = ""
    if delta is not None:
        color = "green" if delta >= 0 else "red"
        sign = "+" if delta >= 0 else ""
        delta_html = f"<div class='kpi-delta' style='color:{color}'>{sign}{delta:.2f}%</div>"

    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>{emoji} {title}</div>
        <div class='kpi-value'>{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)



mean_val = df[column].mean()
median_val = df[column].median()
std_val = df[column].std()

col1, col2, col3 = st.columns(3)
col1.metric("Mean", f"{mean_val:,.2f}")
col2.metric("Median", f"{median_val:,.2f}")
col3.metric("Std Dev", f"{std_val:,.2f}")

# ----------------------------
# Visualizations
# ----------------------------
st.subheader(f"📈 Distribution of {column}")

c1, c2 = st.columns(2)

with c1:
    fig_hist = px.histogram(
        df,
        x=column,
        nbins=30,
        title="Histogram"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with c2:
    fig_box = px.box(
        df,
        y=column,
        title="Box Plot"
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ----------------------------
# Descriptive Statistics Table
# ----------------------------
st.subheader("📊 Descriptive Statistics")

stats_df = df[column].describe().to_frame().rename(columns={column: "Value"})
st.table(stats_df)

# ----------------------------
# Grouped Statistics (Optional)
# ----------------------------
st.subheader("📌 Grouped Statistics (Age Bins)")

df["Age Group"] = pd.cut(df["Age"], bins=[20, 30, 40, 50, 60])

group_stats = df.groupby("Age Group")[column].agg(
    ["mean", "median", "std", "min", "max"]
)

st.dataframe(group_stats, use_container_width=True)



# KPI 
selected_col = st.selectbox(
    "Select Metric",
    df.select_dtypes(include=np.number).columns
)

current_mean = df[selected_col].mean()
previous_mean = current_mean * np.random.uniform(0.9, 1.1)  # Simulated trend
delta = ((current_mean - previous_mean) / previous_mean) * 100

col1, col2, col3 = st.columns(3)

with col1:
    kpi_card(
        "Average",
        f"{current_mean:,.2f}",
        delta,
        "📈"
    )

with col2:
    kpi_card(
        "Median",
        f"{df[selected_col].median():,.2f}",
        None,
        "📊"
    )

with col3:
    kpi_card(
        "Std Deviation",
        f"{df[selected_col].std():,.2f}",
        None,
        "📉"
    )
