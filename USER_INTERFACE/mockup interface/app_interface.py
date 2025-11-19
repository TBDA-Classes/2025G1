import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# 🛑 1. IMPORT DU SERVICE DE DONNÉES (Assurez-vous que data_service.py est dans le chemin)
from data_service import get_state_times, get_energy_consumption

# -----------------------------
# BASIC PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="CNC Monitoring Dashboard",
    layout="wide"
)

# -----------------------------
# FAKE / SAMPLE DATA GENERATION (CONSERVÉES POUR LA SIMULATION DES DONNÉES GRANULAIRES)
# -----------------------------
np.random.seed(42)

# Example machines & programs
MACHINES = ["Machine A", "Machine B", "Machine C"]
PROGRAMS = ["Prog_01", "Prog_02", "Prog_03", "Prog_04"]

# Create a small fake dataset for the last 7 days
today = datetime.today().date()
dates = [today - timedelta(days=i) for i in range(6, -1, -1)]

# Définition de la période par défaut
DEFAULT_START_DATE = (today - timedelta(days=6)).strftime("%Y-%m-%d 00:00:00")
DEFAULT_END_DATE = today.strftime("%Y-%m-%d 23:59:59")


# Fonctions de génération de données factices (non modifiées)
def generate_program_execution_data():
    # ... (Code existant pour program_df) ...
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

def generate_time_data():
    # ... (Code existant pour time_df) ...
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

def generate_energy_data():
    # ... (Code existant pour energy_df) ...
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

def generate_status_timeline():
    # ... (Code existant pour status_df) ...
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

# DataFrames globaux
program_df = generate_program_execution_data()
status_df = generate_status_timeline()


# -----------------------------
# 🛑 2. FONCTIONS DE CHARGEMENT DU BACKEND (NOUVEAU)
# -----------------------------

@st.cache_data
def get_backend_time_data(from_date: str, until_date: str):
    """
    Appel réel au backend pour obtenir les totaux des temps d'activité/inactivité.
    Utilise get_state_times.
    """
    # 1. Appel du service réel (COMMENTEZ CETTE LIGNE si vous utilisez la SIMULATION ci-dessous)
    # result = get_state_times(from_date, until_date) 
    
    # --- SIMULATION TEMPORAIRE ---
    # Nous utilisons la fonction factice pour simuler des données granulaires nécessaires aux graphiques.
    df_time_full = generate_time_data() 
    
    # Filtrer les données factices selon la plage de dates
    start_dt = datetime.strptime(from_date.split(" ")[0], "%Y-%m-%d").date()
    end_dt = datetime.strptime(until_date.split(" ")[0], "%Y-%m-%d").date()
    
    df_filtered = df_time_full[
        (df_time_full["date"] >= start_dt) &
        (df_time_full["date"] <= end_dt)
    ]
    # -----------------------------
    
    return df_filtered

@st.cache_data
def get_backend_energy_data(from_date: str, until_date: str):
    """
    Appel réel au backend pour obtenir les données d'énergie.
    Utilise get_energy_consumption.
    """
    # 1. Appel du service réel (COMMENTEZ CETTE LIGNE si vous utilisez la SIMULATION ci-dessous)
    # result = get_energy_consumption(from_date, until_date) 
    
    # --- SIMULATION TEMPORAIRE ---
    df_energy_full = generate_energy_data()
    
    start_dt = datetime.strptime(from_date.split(" ")[0], "%Y-%m-%d").date()
    end_dt = datetime.strptime(until_date.split(" ")[0], "%Y-%m-%d").date()
    
    df_filtered = df_energy_full[
        (df_energy_full["date"] >= start_dt) &
        (df_energy_full["date"] <= end_dt)
    ]
    # -----------------------------
    
    return df_filtered

# Chargement des données initiales (avec les fonctions de backend)
time_df = get_backend_time_data(DEFAULT_START_DATE, DEFAULT_END_DATE)
energy_df = get_backend_energy_data(DEFAULT_START_DATE, DEFAULT_END_DATE)


# -----------------------------
# KPI HELPER FUNCTIONS (Non modifiées)
# -----------------------------
def compute_high_level_kpis():
    # ... (Reste inchangé) ...
    planned_time = 8 * len(MACHINES)  # hours/day * machines
    # Utilisation du time_df global chargé par le backend (via simulation)
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

def status_emoji(value, good_threshold, warning_threshold):
    # ... (Reste inchangé) ...
    if value >= good_threshold:
        return "🟢"
    elif value >= warning_threshold:
        return "🟠"
    else:
        return "🔴"

# -----------------------------
# PAGE RENDERING FUNCTIONS (MODIFIÉES POUR UTILISER LES FILTRES ET LE BACKEND)
# -----------------------------
def render_home():
    st.title("🏠 Home - CNC Monitoring Overview")
    # ... (Reste inchangé) ...
    kpis = compute_high_level_kpis()

    st.subheader("Global KPIs (Demo Values)")
    # ... (Affichage des KPI) ...

    st.markdown("---")
    st.subheader("Machine Utilization Summary (Current Period - Demo)")
    # ... (Affichage de l'utilisation) ...

    st.markdown("---")
    st.subheader("Machine Status Timeline (Today - Demo)")
    # ... (Affichage de la timeline) ...
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

    st.markdown("This tab shows **Operational KPIs** such as Program Execution Count, Average Program Duration, Operating Time and Standby Time.")

    # Filters
    st.subheader("Filters")

    col1, col2 = st.columns(2)
    with col1:
        selected_machine = st.selectbox("Machine", ["All"] + MACHINES)
    with col2:
        min_date = min(dates)
        max_date = max(dates)
        date_range_date = st.slider(
            "Date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )
        
    # 🛑 3. MISE À JOUR : Appel du backend avec les dates sélectionnées
    start_dt_str = date_range_date[0].strftime("%Y-%m-%d 00:00:00")
    end_dt_str = date_range_date[1].strftime("%Y-%m-%d 23:59:59")
    
    # CHARGEMENT DU TEMPS DE TRAVAIL DEPUIS LE BACKEND
    df_time = get_backend_time_data(start_dt_str, end_dt_str)
    
    # Filtrage des autres DataFrames pour cohérence (doivent être remplacés par des appels backend)
    df_prog = program_df[
        (program_df["date"] >= date_range_date[0]) &
        (program_df["date"] <= date_range_date[1])
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
    # ... (Code inchangé utilisant df_prog) ...
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
    # ... (Code inchangé utilisant df_prog) ...
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

    # 🛑 Le chart utilise maintenant df_time, qui est chargé depuis le backend
    if not df_time.empty:
        # Convert to long format for stacked bar chart
        df_melt = df_time.melt(
            id_vars=["date", "machine"],
            value_vars=["Operating", "Standby"],
            var_name="Status",
            value_name="Hours"
        )
        # ... (Code inchangé utilisant df_melt) ...
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
        st.caption("Stacked bar chart showing Operating vs Standby time.")
    else:
        st.info("No time data to display.")


def render_energy_monitoring():
    st.title("🔌 Energy Monitoring")

    st.markdown("This tab shows **Energy-related KPIs**.")

    # Filters
    st.subheader("Filters")

    col1, col2 = st.columns(2)
    with col1:
        selected_machine = st.selectbox("Machine", ["All"] + MACHINES, key="energy_machine")
    with col2:
        min_date = min(dates)
        max_date = max(dates)
        date_range_date = st.slider(
            "Date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            key="energy_dates"
        )
        
    # 🛑 4. MISE À JOUR : Appel du backend avec les dates sélectionnées
    start_dt_str = date_range_date[0].strftime("%Y-%m-%d 00:00:00")
    end_dt_str = date_range_date[1].strftime("%Y-%m-%d 23:59:59")
    
    # CHARGEMENT DES DONNÉES D'ÉNERGIE DEPUIS LE BACKEND
    df_energy = get_backend_energy_data(start_dt_str, end_dt_str)

    # Filtrage des DataFrames factices restants pour cohérence
    df_prog = program_df[
        (program_df["date"] >= date_range_date[0]) &
        (program_df["date"] <= date_range_date[1])
    ]
    df_time = get_backend_time_data(start_dt_str, end_dt_str)


    if selected_machine != "All":
        df_energy = df_energy[df_energy["machine"] == selected_machine]
        df_prog = df_prog[df_prog["machine"] == selected_machine]
        df_time = df_time[df_time["machine"] == selected_machine]


    # ------------------ KPIs (cards) ------------------
    st.markdown("### Energy KPIs")

    total_energy = df_energy["total_energy_kwh"].sum() if not df_energy.empty else 0
    total_operating_hours = df_time["Operating"].sum()
    energy_per_operating_h = total_energy / total_operating_hours if total_operating_hours > 0 else 0

    # Fake energy per program logic (non modifié)
    total_programs = len(df_prog) if not df_prog.empty else 0
    energy_per_program = total_energy / total_programs if total_programs > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        emoji = status_emoji(total_energy, 0, 0)
        st.metric("Total Energy (kWh)", f"{total_energy:.1f}")
        st.caption("Total energy consumption over selected period.")
    with col2:
        st.metric("Energy per Operating Hour (kWh/h)", f"{energy_per_operating_h:.2f}")
        st.caption("Total energy divided by total operating hours.")
    with col3:
        st.metric("Energy per Program (kWh/program)", f"{energy_per_program:.2f}")
        st.caption("Approximate indicator using demo logic.")

    # ------------------ Line chart: Total energy over time (non modifié) ------------------
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

    # ------------------ Bar chart: Energy by program (demo) (non modifié) ------------------
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
# SIDEBAR NAVIGATION (Non modifiée)
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