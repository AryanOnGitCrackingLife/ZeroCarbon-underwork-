import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="ZeroCarbon Analytics",
    layout="wide",
    page_icon="🌱"
)

# ================= THEME & CSS =================
st.markdown("""
<style>
/* Background */
.stApp {
    background: #f5f7fa;
}

/* Remove Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}

/* Header */
.header {
    background: linear-gradient(135deg, #0B3D2E, #1F6F8B);
    padding: 30px;
    border-radius: 18px;
    margin-bottom: 30px;
    color: white;
    text-align: center;
}
.header h1 {
    margin-bottom: 6px;
    font-size: 34px;
}
.header p {
    opacity: 0.9;
}

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
.metric-title {
    color: #6b7280;
    font-size: 14px;
}
.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: #16a34a;
    margin-top: 6px;
}

/* Section */
.section {
    margin-top: 30px;
}
.section h3 {
    color: #1f2933;
    margin-bottom: 12px;
}

/* Chart container */
.chart-box {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

/* Info text */
.muted {
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# ================= DB =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
conn = sqlite3.connect(DB_PATH)

def load(table):
    try:
        df = pd.read_sql(f"SELECT date, carbon_kg FROM {table}", conn)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except:
        return pd.DataFrame(columns=["date", "carbon_kg"])

food = load("dashboard_foodconsumption")
electricity = load("dashboard_electricityusage")
travel = load("dashboard_travel")
waste = load("dashboard_wastesegregation")

# ================= HEADER =================
st.markdown("""
<div class="header">
    <h1>🌱 ZeroCarbon Analytics</h1>
    <p>Visual insights into your carbon footprint</p>
</div>
""", unsafe_allow_html=True)

# ================= METRICS =================
totals = {
    "Food": food["carbon_kg"].sum(),
    "Electricity": electricity["carbon_kg"].sum(),
    "Travel": travel["carbon_kg"].sum(),
    "Waste": waste["carbon_kg"].sum(),
}

m1, m2, m3, m4 = st.columns(4)
for col, (k, v) in zip([m1, m2, m3, m4], totals.items()):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{k}</div>
        <div class="metric-value">{v:.2f} kg</div>
    </div>
    """, unsafe_allow_html=True)

# ================= CHARTS ROW 1 =================

st.markdown('<div class="section"><h3>📊 Emissions Overview</h3></div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    if sum(totals.values()) > 0:
        fig, ax = plt.subplots(figsize=(4.5,4.5))
        ax.pie(
            totals.values(),
            labels=totals.keys(),
            autopct="%1.1f%%",
            startangle=90,
            colors=["#22c55e", "#3b82f6", "#facc15", "#f97316"]
        )
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("No data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    if sum(totals.values()) > 0:
        fig, ax = plt.subplots(figsize=(5,3.5))
        ax.bar(totals.keys(), totals.values(), color="#22c55e")
        ax.set_ylabel("kg CO₂")
        st.pyplot(fig)
    else:
        st.info("No data available.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TIMELINE =================
timeline = pd.concat([
    food.assign(category="Food"),
    electricity.assign(category="Electricity"),
    travel.assign(category="Travel"),
    waste.assign(category="Waste"),
])

st.markdown('<div class="section"><h3>📈 Emission Trends</h3></div>', unsafe_allow_html=True)

c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    fe = timeline[timeline["category"].isin(["Food", "Electricity"])]
    if not fe.empty:
        st.line_chart(fe.groupby("date")["carbon_kg"].sum(), height=240)
    else:
        st.info("No data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    tw = timeline[timeline["category"].isin(["Travel", "Waste"])]
    if not tw.empty:
        st.line_chart(tw.groupby("date")["carbon_kg"].sum(), height=240)
    else:
        st.info("No data available.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= PROGRESS =================
st.markdown('<div class="section"><h3>📉 Overall Progress</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="chart-box">', unsafe_allow_html=True)

daily = timeline.groupby("date")["carbon_kg"].sum().sort_index()
if len(daily) > 1:
    change = daily.iloc[-1] - daily.iloc[0]
    percent = (change / daily.iloc[0]) * 100 if daily.iloc[0] != 0 else 0
    if percent < 0:
        st.success(f"🎉 Emissions reduced by {abs(percent):.2f}%")
    else:
        st.warning(f"⚠️ Emissions increased by {percent:.2f}%")
else:
    st.info("Not enough data yet.")

st.markdown('</div>', unsafe_allow_html=True)

conn.close()
