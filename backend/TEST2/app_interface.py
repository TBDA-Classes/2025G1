import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta
from data_service import get_state_times, get_energy_consumption

# -----------------------------
# BASIC PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="CNC Monitoring Dashboard",
    layout="wide"
)

# -----------------------------
# FAKE / SAMPLE DATA GENERATION
# -----------------------------
np.random.seed(42)

# Example machines & programs
MACHINES = ["Machine A", "Machine B", "Machine C"]
PROGRAMS = ["Prog_01", "Prog_02", "Prog_03", "Prog_04"]

# Create a small fake dataset for the last 7 days
today = datetime.today().date()
dates = [today - timedelta(days=i) for i in range(6, -1, -1)]

# Sample program execution data
def generate_program_execution_data():
    rows = []
    for d in dates:
        for machine in MACHINES:
            for prog in PROGRAMS:
                runs = np.random.randint(0, 8)  # 0-7 runs per day/program
                for _ in range(runs):
                    duration_min = np.random.normal(loc=25, scale=8)  # avg duration ~25 min
                    duration_min = max(5, duration_min)  # no negative
                    rows.append({
                        "date": d,
                        "machine": machine,
                        "program": prog,
                        "duration_min": duration_min
                    })
    return pd.DataFrame(rows)

program_df = generate_program_execution_data()

# Sample operating / standby time data (per day & machine)
def generate_time_data():
    rows = []
    for d in dates:
        for machine in MACHINES:
            total_shift_hours = 8
            operating = np.random.uniform(3, 7)
            standby = max(0, total_shift_hours - operating - np.random.uniform(0, 2))
            rows.append({
                "date": d,
                "machine": machine,
                "Operating": operating,
                "Standby": standby
            })
    return pd.DataFrame(rows)

time_df = generate_time_data()

# Sample energy data
def generate_energy_data():
    rows = []
    for d in dates:
        for machine in MACHINES:
            base_energy = np.random.uniform(80, 150)  # kWh per day
            rows.append({
                "date": d,
                "machine": machine,
                "total_energy_kwh": base_energy,
                "energy_per_operating_h": base_energy / np.random.uniform(3, 7),
            })
    return pd.DataFrame(rows)

energy_df = generate_energy_data()

# Sample machine status timeline (for today)
def generate_status_timeline():
    statuses = ["Operating", "Standby", "Alarm", "Off"]
    segments = []
    current_time = datetime.combine(today, datetime.min.time())
    for _ in range(24):  # 24 segments (1h each)
        status = np.random.choice(statuses, p=[0.5, 0.3, 0.1, 0.1])
        duration_h = 1
        segments.append({
            "start": current_time,
            "end": current_time + timedelta(hours=duration_h),
            "status": status,
            "duration_h": duration_h
        })
        current_time += timedelta(hours=duration_h)
    return pd.DataFrame(segments)

status_df = generate_status_timeline()

# -----------------------------
# KPI HELPER FUNCTIONS
# -----------------------------
def compute_high_level_kpis():
    # Totally fake but consistent logic for demo
    planned_time = 8 * len(MACHINES)  # hours/day * machines
    operating_time = time_df["Operating"].sum()
    downtime = (planned_time * len(dates)) - operating_time

    availability = operating_time / (planned_time * len(dates))
    performance = np.random.uniform(0.85, 0.98)
    quality = np.random.uniform(0.90, 0.99)
    oee = availability * performance * quality

    return {
        "OEE": oee * 100,
        "Availability": availability * 100,
        "Performance": performance * 100,
        "Quality": quality * 100,
        "Planned Time (h)": planned_time * len(dates),
        "Run Time (h)": operating_time,
        "Idle/Down Time (h)": downtime
    }

# Simple helper for “traffic light” emojis
def status_emoji(value, good_threshold, warning_threshold):
    if value >= good_threshold:
        return "🟢"
    elif value >= warning_threshold:
        return "🟠"
    else:
        return "🔴"

# -----------------------------
# PAGE RENDERING FUNCTIONS
# -----------------------------
def render_home():
    st.title("🏠 Home - CNC Monitoring Overview")

    kpis = compute_high_level_kpis()

    st.subheader("Global KPIs (Demo Values)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emoji = status_emoji(kpis["OEE"], 80, 60)
        st.metric("OEE (%)", f"{kpis['OEE']:.1f}")
        st.caption(f"{emoji} Overall Equipment Effectiveness")
    with col2:
        emoji = status_emoji(kpis["Availability"], 85, 70)
        st.metric("Availability (%)", f"{kpis['Availability']:.1f}")
        st.caption(f"{emoji} Availability = Operating / Planned")
    with col3:
        emoji = status_emoji(kpis["Performance"], 90, 75)
        st.metric("Performance (%)", f"{kpis['Performance']:.1f}")
        st.caption(f"{emoji} Speed vs Ideal Cycle Time")
    with col4:
        emoji = status_emoji(kpis["Quality"], 95, 90)
        st.metric("Quality (%)", f"{kpis['Quality']:.1f}")
        st.caption(f"{emoji} Good Parts vs Total")

    st.markdown("---")
    st.subheader("Machine Utilization Summary (Current Period - Demo)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Planned Time (h)", f"{kpis['Planned Time (h)']:.1f}")
    with col2:
        st.metric("Run Time (h)", f"{kpis['Run Time (h)']:.1f}")
    with col3:
        st.metric("Idle/Down Time (h)", f"{kpis['Idle/Down Time (h)']:.1f}")
    with col4:
        util = kpis["Run Time (h)"] / kpis["Planned Time (h)"] * 100
        st.metric("Utilization (%)", f"{util:.1f}")

    st.markdown("---")
    st.subheader("Machine Status Timeline (Today - Demo)")

    # Create a timeline-like bar chart
    chart_data = status_df.copy()
    chart_data["start_time"] = chart_data["start"].dt.strftime("%H:%M")

    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("start_time:N", title="Time of Day"),
            y=alt.Y("duration_h:Q", title="Duration (h)"),
            color=alt.Color("status:N", title="Status"),
            tooltip=["status", "start_time", "duration_h"]
        )
    )

    st.altair_chart(chart, use_container_width=True)
    st.caption("Each bar represents 1 hour with its machine status (Operating, Standby, Alarm, Off).")


def render_operation_monitoring():
    st.title("⚙️ Operation Monitoring")

    st.markdown("This tab shows **Operational KPIs** such as Program Execution Count, Average Program Duration, Operating Time and Standby Time (using demo data).")

    # Filters
    st.subheader("Filters")

    col1, col2 = st.columns(2)
    with col1:
        selected_machine = st.selectbox("Machine", ["All"] + MACHINES)
    with col2:
        min_date = min(dates)
        max_date = max(dates)
        date_range = st.slider(
            "Date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )

    # Filter program_df and time_df
    df_prog = program_df[
        (program_df["date"] >= date_range[0]) &
        (program_df["date"] <= date_range[1])
    ]
    df_time = time_df[
        (time_df["date"] >= date_range[0]) &
        (time_df["date"] <= date_range[1])
    ]

    if selected_machine != "All":
        df_prog = df_prog[df_prog["machine"] == selected_machine]
        df_time = df_time[df_time["machine"] == selected_machine]

    # ------------------ KPIs (numbers) ------------------
    st.markdown("### Program KPIs")

    total_program_runs = len(df_prog)
    avg_prog_duration = df_prog["duration_min"].mean() if not df_prog.empty else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Program Execution Count", total_program_runs)
    with col2:
        st.metric("Average Program Duration (min)", f"{avg_prog_duration:.1f}")

    # Column chart: Program Execution Count by day
    st.markdown("#### Program Execution Count per Day")

    if not df_prog.empty:
        exec_per_day = (
            df_prog.groupby("date")["program"]
            .count()
            .reset_index(name="program_count")
        )
        bar_chart = (
            alt.Chart(exec_per_day)
            .mark_bar()
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("program_count:Q", title="Number of Programs"),
                tooltip=["date", "program_count"]
            )
        )
        st.altair_chart(bar_chart, use_container_width=True)
    else:
        st.info("No program executions in the selected period.")

    # Box plot: Average Program Duration distribution
    st.markdown("#### Program Duration Distribution (Box Plot)")

    if not df_prog.empty:
        box_chart = (
            alt.Chart(df_prog)
            .mark_boxplot()
            .encode(
                x=alt.X("machine:N", title="Machine"),
                y=alt.Y("duration_min:Q", title="Program Duration (min)"),
                tooltip=["machine", "duration_min"]
            )
        )
        st.altair_chart(box_chart, use_container_width=True)
    else:
        st.info("No duration data to display.")

    # ------------------ Operating & Standby Time ------------------
    st.markdown("---")
    st.markdown("### Operating vs Standby Time")

    if not df_time.empty:
        # Convert to long format for stacked bar chart
        df_melt = df_time.melt(
            id_vars=["date", "machine"],
            value_vars=["Operating", "Standby"],
            var_name="Status",
            value_name="Hours"
        )

        stacked_chart = (
            alt.Chart(df_melt)
            .mark_bar()
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("Hours:Q", stack="zero", title="Hours"),
                color=alt.Color("Status:N", title="Status"),
                tooltip=["date", "machine", "Status", "Hours"]
            )
        )

        st.altair_chart(stacked_chart, use_container_width=True)

        st.caption("Stacked bar chart showing Operating (green in real implementation) vs Standby (red) time.")
    else:
        st.info("No time data to display.")


def render_energy_monitoring():
    st.title("🔌 Energy Monitoring")

    st.markdown("This tab shows **Energy-related KPIs** using demo data (Total energy, Energy per operating hour, Energy per program, etc.).")

    # Filters
    st.subheader("Filters")

    col1, col2 = st.columns(2)
    with col1:
        selected_machine = st.selectbox("Machine", ["All"] + MACHINES, key="energy_machine")
    with col2:
        min_date = min(dates)
        max_date = max(dates)
        date_range = st.slider(
            "Date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            key="energy_dates"
        )

    df_energy = energy_df[
        (energy_df["date"] >= date_range[0]) &
        (energy_df["date"] <= date_range[1])
    ]

    if selected_machine != "All":
        df_energy = df_energy[df_energy["machine"] == selected_machine]

    # Fake “energy per program” using program_df just for visualization
    df_prog = program_df[
        (program_df["date"] >= date_range[0]) &
        (program_df["date"] <= date_range[1])
    ]
    if selected_machine != "All":
        df_prog = df_prog[df_prog["machine"] == selected_machine]

    # ------------------ KPIs (cards) ------------------
    st.markdown("### Energy KPIs")

    total_energy = df_energy["total_energy_kwh"].sum() if not df_energy.empty else 0
    total_operating_hours = time_df["Operating"].sum()
    energy_per_operating_h = total_energy / total_operating_hours if total_operating_hours > 0 else 0

    # Fake energy per program: assume each program has same share of total energy
    total_programs = len(df_prog) if not df_prog.empty else 0
    energy_per_program = total_energy / total_programs if total_programs > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        emoji = status_emoji(total_energy, 0, 0)  # for demo, no threshold
        st.metric("Total Energy (kWh)", f"{total_energy:.1f}")
        st.caption("Total energy consumption over selected period.")
    with col2:
        st.metric("Energy per Operating Hour (kWh/h)", f"{energy_per_operating_h:.2f}")
        st.caption("Total energy divided by total operating hours.")
    with col3:
        st.metric("Energy per Program (kWh/program)", f"{energy_per_program:.2f}")
        st.caption("Approximate indicator using demo logic.")

    # ------------------ Line chart: Total energy over time ------------------
    st.markdown("### Total Energy Consumption Over Time")

    if not df_energy.empty:
        energy_by_date = (
            df_energy.groupby("date")["total_energy_kwh"]
            .sum()
            .reset_index()
        )
        line_chart = (
            alt.Chart(energy_by_date)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("total_energy_kwh:Q", title="Energy (kWh)"),
                tooltip=["date", "total_energy_kwh"]
            )
        )
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.info("No energy data to display for the selected period.")

    # ------------------ Bar chart: Energy by program (demo) ------------------
    st.markdown("### Energy by Program (Demo)")

    if not df_prog.empty and total_energy > 0:
        prog_counts = (
            df_prog.groupby("program")["program"]
            .count()
            .reset_index(name="count")
        )
        prog_counts["energy_kwh"] = (
            prog_counts["count"] / prog_counts["count"].sum()
        ) * total_energy

        bar_chart = (
            alt.Chart(prog_counts)
            .mark_bar()
            .encode(
                x=alt.X("program:N", title="Program"),
                y=alt.Y("energy_kwh:Q", title="Estimated Energy (kWh)"),
                tooltip=["program", "energy_kwh"]
            )
        )
        st.altair_chart(bar_chart, use_container_width=True)
        st.caption("Programs with higher bars are more energy-intensive (demo logic).")
    else:
        st.info("Not enough data to estimate energy per program.")


# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("CNC Dashboard")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Operation Monitoring", "Energy Monitoring"]
)

if page == "Home":
    render_home()
elif page == "Operation Monitoring":
    render_operation_monitoring()
elif page == "Energy Monitoring":
    render_energy_monitoring()
