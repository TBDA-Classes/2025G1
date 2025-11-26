import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

# 🛑 IMPORT REAL DATA SERVICE
from data_service import get_state_times, get_energy_consumption, get_machine_alarms

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="CNC Analytics - Professional Dashboard",
    layout="wide",
    page_icon="🏭"
)

# -----------------------------
# MODERN PROFESSIONAL THEME & CSS
# -----------------------------
# Primary Color: #0F172A (Slate Blue - Professional Dark)
# Accent Color: #3B82F6 (Bright Blue - Tech/Active)
# Success: #10B981 (Emerald Green)
# Warning: #F59E0B (Amber)
# Background: #F8FAFC (Very light cool grey)

st.markdown(
    """
    <style>
    /* --- GLOBAL SETTINGS --- */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: #1E293B;
    }

    /* --- HEADERS --- */
    h1, h2, h3 {
        color: #0F172A !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    h1 { font-size: 2.2rem; }
    h3 { font-size: 1.3rem; margin-top: 20px; }

    /* --- METRICS (KPI CARDS) --- */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricLabel"] {
        color: #64748B; /* Muted Text */
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A;
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }
    
    /* --- ALERTS --- */
    .stAlert {
        border-radius: 8px;
    }

    /* --- LOGO CONTAINER --- */
    .logo-container {
        display: flex;
        align-items: center;
        padding: 20px 0;
        border-bottom: 1px solid #CBD5E1;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# DATE CONFIGURATION
# -----------------------------
MIN_DATE = date(2020, 12, 28)
MAX_DATE = date(2022, 2, 23)
DEFAULT_START_DATE = date(2022, 1, 23)
DEFAULT_END_DATE = MAX_DATE

# -----------------------------
# DATA LOADING FUNCTIONS (CACHED)
# -----------------------------
@st.cache_data(ttl=600)
def load_state_data(start_str, end_str):
    return get_state_times(start_str, end_str)

@st.cache_data(ttl=600)
def load_energy_data(start_str, end_str):
    return get_energy_consumption(start_str, end_str)

@st.cache_data(ttl=600)
def load_alarm_data(start_str, end_str):
    return get_machine_alarms(start_str, end_str)

# -----------------------------
# SIDEBAR
# -----------------------------
# Modern Logo (SVG)
logo_svg = """
<svg width="280" height="80" viewBox="0 0 300 80" xmlns="http://www.w3.org/2000/svg">
  <path d="M40 10 L70 25 L70 55 L40 70 L10 55 L10 25 Z" fill="#3B82F6" />
  <path d="M40 20 L60 30 L60 50 L40 60 L20 50 L20 30 Z" fill="#ffffff" opacity="0.3"/>
  <circle cx="40" cy="40" r="8" fill="#FFFFFF" />
  
  <text x="85" y="48" font-family="sans-serif" font-size="32" fill="#0F172A" font-weight="bold" letter-spacing="-1">CNC</text>
  <text x="155" y="48" font-family="sans-serif" font-size="32" fill="#64748B" font-weight="300">VISION</text>
</svg>
"""
st.sidebar.markdown(logo_svg, unsafe_allow_html=True)

st.sidebar.subheader("📅 Timeframe Selection")
date_range = st.sidebar.date_input(
    "Analysis Period",
    value=(DEFAULT_START_DATE, DEFAULT_END_DATE),
    min_value=MIN_DATE,
    max_value=MAX_DATE
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    f_start = f"{start_date} 00:00:00"
    f_end = f"{end_date} 23:59:59"
else:
    st.sidebar.warning("Please select a start and end date.")
    st.stop()

page = st.sidebar.radio(
    "DASHBOARD MODULES",
    ["Overview & States", "Alarms & Diagnostics", "Energy Consumption"]
)

st.sidebar.markdown("---")
st.sidebar.caption(f"🟢 System Online\nData Range: {MIN_DATE} to {MAX_DATE}")

# -----------------------------
# PAGE 1: OVERVIEW & STATES
# -----------------------------
def render_home():
    st.title("Overview & Machine States")
    st.markdown("Operational efficiency and time distribution analysis.")

    # 1. Load Data
    with st.spinner("Fetching metrics..."):
        df_states = load_state_data(f_start, f_end)

    if df_states.empty:
        st.info("No data available for this period.")
        return

    # 2. Global KPIs
    total_hours = df_states["total_hours"].sum()
    
    try:
        idle_hours = df_states[df_states['state'].str.contains("Idle", case=False, na=False)]['total_hours'].sum()
        active_hours = total_hours - idle_hours
        utilization = (active_hours / total_hours * 100) if total_hours > 0 else 0
    except:
        utilization = 0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Monitored Time", f"{total_hours:,.1f} h")
    with col2:
        st.metric("Active Utilization", f"{utilization:.1f} %", delta_color="normal")
    with col3:
        st.metric("Distinct States", len(df_states))

    st.markdown("---")

    # 3. Donut Chart (Clean Professional Colors)
    st.subheader("Time Distribution")
    
    # Professional Palette:
    # High = Green, Medium = Teal, Low = Blue, Idle = Light Grey
    state_colors = alt.Scale(
        domain=['High Activity', 'Intermediate Activity', 'Low Activity', 'True Idle (Off)'],
        range=['#10B981', '#3B82F6', '#6366F1', '#CBD5E1'] 
    )

    base = alt.Chart(df_states).encode(
        theta=alt.Theta("total_hours", stack=True)
    )

    pie = base.mark_arc(outerRadius=120, innerRadius=75).encode(
        color=alt.Color("state", scale=state_colors, legend=alt.Legend(title="Status")),
        order=alt.Order("total_hours", sort="descending"),
        tooltip=["state", alt.Tooltip("total_hours", format=".1f")]
    )

    # --- FIXED: Styling parameters moved to mark_text() ---
    text = base.mark_text(radius=145, fill="#0F172A", fontSize=12).encode(
        text=alt.Text("total_hours", format=".0f"),
        order=alt.Order("total_hours", sort="descending")
    )

    st.altair_chart(pie + text, use_container_width=True)
    
    with st.expander("View Raw Data"):
        st.dataframe(df_states, use_container_width=True)

# -----------------------------
# PAGE 2: ALARMS & DIAGNOSTICS
# -----------------------------
def render_alarms():
    st.title("Alarms & Diagnostics")
    st.markdown("Critical mechanical faults and safety stops (filtered for noise).")

    with st.spinner("Analyzing alarm logs..."):
        df_alarms = load_alarm_data(f_start, f_end)

    if df_alarms.empty:
        st.success("✅ No critical alarms found in this range.")
        return

    total_occurrences = df_alarms["occurrence_count"].sum()
    unique_alarms = len(df_alarms)
    top_alarm_code = df_alarms.iloc[0]["alarm_code"]
    top_alarm_text = df_alarms.iloc[0]["alarm_text"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Alert Events", total_occurrences)
    with col2:
        st.metric("Unique Error Types", unique_alarms)

    st.warning(f"**Most Frequent Issue:** {top_alarm_code} — {top_alarm_text}")

    st.markdown("---")

    st.subheader("Top 10 Frequent Faults")

    # Modern Horizontal Bar Chart
    chart = (
        alt.Chart(df_alarms.head(10))
        .mark_bar(cornerRadius=4, height=25)
        .encode(
            x=alt.X("occurrence_count:Q", title="Count"),
            y=alt.Y("alarm_text:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
            color=alt.value("#EF4444"), # Modern Red
            tooltip=["alarm_code", "alarm_text", "occurrence_count", "last_seen"]
        )
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Detailed Log")
    st.dataframe(
        df_alarms,
        use_container_width=True,
        column_config={
            "last_seen": st.column_config.DatetimeColumn("Last Detected", format="MMM D, YYYY - HH:mm"),
            "occurrence_count": st.column_config.ProgressColumn("Frequency", format="%d", min_value=0, max_value=int(df_alarms["occurrence_count"].max())),
            "alarm_code": "Error Code",
            "alarm_text": "Description"
        }
    )

# -----------------------------
# PAGE 3: ENERGY CONSUMPTION
# -----------------------------
def render_energy():
    st.title("Energy Consumption")
    st.markdown("Electrical power tracking (kWh).")

    with st.spinner("Loading energy metrics..."):
        df_energy = load_energy_data(f_start, f_end)

    if df_energy.empty:
        st.info("No energy data available for this period.")
        return

    total_kwh = df_energy["total_energy_kwh"].sum()
    avg_daily = df_energy["total_energy_kwh"].mean()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Consumption", f"{total_kwh:,.0f} kWh")
    with col2:
        st.metric("Daily Average", f"{avg_daily:,.1f} kWh")

    st.markdown("---")

    st.subheader("Daily Consumption Trend")

    # Gradient Area Chart
    line_chart = (
        alt.Chart(df_energy)
        .mark_area(
            line={'color':'#3B82F6'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#3B82F6', offset=0),
                       alt.GradientStop(color='white', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            ),
            opacity=0.6
        )
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("total_energy_kwh:Q", title="Energy (kWh)"),
            tooltip=["date", alt.Tooltip("total_energy_kwh", format=".1f", title="kWh")]
        )
        .properties(height=350)
    )
    st.altair_chart(line_chart, use_container_width=True)

# -----------------------------
# MAIN ROUTING
# -----------------------------
if page == "Overview & States":
    render_home()
elif page == "Alarms & Diagnostics":
    render_alarms()
elif page == "Energy Consumption":
    render_energy()