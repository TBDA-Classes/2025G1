import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# ----------------------------------
# 1. IMPORT BACKEND DATA SERVICES
# ----------------------------------
# Assure-toi que ce fichier existe bien localement
from data_service import (
    get_state_times,
    get_machine_alarms,
    get_energy_consumption,
)

# ----------------------------------
# 2. COMPAT CACHE
# ----------------------------------
def cache_data(*args, **kwargs):
    if hasattr(st, "cache_data"):
        return st.cache_data(*args, **kwargs)
    elif hasattr(st, "cache"):
        return st.cache(*args, **kwargs)
    def decorator(func):
        return func
    return decorator

# ----------------------------------
# 3. PAGE CONFIG & DATES PAR DÉFAUT (OPTIMISÉ)
# ----------------------------------
st.set_page_config(
    page_title="CNC Monitoring Dashboard",
    layout="wide"
)

# OPTIMISATION : On ne scanne plus la DB depuis l'an 2000 au démarrage.
# On fixe une vue par défaut sur les 7 ou 30 derniers jours.
# Cela rend le chargement de la page quasi instantané.
today = date.today()
DEFAULT_END_DATE: date = today
DEFAULT_START_DATE: date = today - timedelta(days=7) 

def to_backend_datetime_str(d: date, start_of_day: bool = True) -> str:
    """Format YYYY-MM-DD HH:MM:SS"""
    if start_of_day:
        return f"{d.strftime('%Y-%m-%d')} 00:00:00"
    else:
        return f"{d.strftime('%Y-%m-%d')} 23:59:59"

# ----------------------------------
# 4. BACKEND WRAPPERS
# ----------------------------------
@cache_data(show_spinner=False)
def load_state_times(from_str: str, until_str: str) -> pd.DataFrame:
    try:
        df = get_state_times(from_str, until_str)
    except Exception as e:
        st.error(f"❌ Error loading state times: {e}")
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]

    if "total_hours" not in df.columns and "hours" in df.columns:
        df = df.rename(columns={"hours": "total_hours"})
    if "state" not in df.columns and "etat" in df.columns:
        df = df.rename(columns={"etat": "state"})
    return df

@cache_data(show_spinner=False)
def load_energy(from_str: str, until_str: str) -> pd.DataFrame:
    try:
        df = get_energy_consumption(from_str, until_str)
    except Exception as e:
        st.error(f"❌ Error loading energy: {e}")
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]

    if "total_energy_kwh" not in df.columns:
        if "total_kwh" in df.columns:
            df = df.rename(columns={"total_kwh": "total_energy_kwh"})
        elif "kwh" in df.columns:
            df = df.rename(columns={"kwh": "total_energy_kwh"})

    # Normalisation dates
    for candidate in ["date", "timestamp", "time", "energy_timestamp"]:
        if candidate in df.columns:
            if candidate != "date":
                df = df.rename(columns={candidate: "date"})
            break
            
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date

    return df

@cache_data(show_spinner=False)
def load_alarms(from_str: str, until_str: str) -> pd.DataFrame:
    try:
        df = get_machine_alarms(from_str, until_str)
    except Exception as e:
        st.error(f"❌ Error loading alarms: {e}")
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    return df

# ----------------------------------
# 5. KPI FUNCTIONS
# ----------------------------------
def compute_state_kpis(df_states: pd.DataFrame) -> dict:
    defaults = {
        "total_hours": 0.0, "active_hours": 0.0, 
        "idle_hours": 0.0, "availability_pct": 0.0
    }
    if df_states.empty: return defaults
    
    col_state = "state"
    col_hours = "total_hours"
    
    if col_state not in df_states.columns or col_hours not in df_states.columns:
        return defaults

    total_hours = float(df_states[col_hours].sum())
    
    # Adapte cette liste selon tes vrais états
    active_states = {"RUN", "ACTIVE", "AUTO", "PRODUCTION", "WORKING"}
    df_states["is_active"] = df_states[col_state].astype(str).str.upper().isin(active_states)
    
    active_hours = float(df_states.loc[df_states["is_active"], col_hours].sum())
    idle_hours = total_hours - active_hours if total_hours > 0 else 0.0
    availability_pct = (active_hours / total_hours * 100.0) if total_hours > 0 else 0.0
    
    return {
        "total_hours": total_hours,
        "active_hours": active_hours,
        "idle_hours": idle_hours,
        "availability_pct": availability_pct,
    }

# ----------------------------------
# 6. PAGES
# ----------------------------------
def render_backend_debug() -> None:
    """
    OPTIMISÉ : Ne check que les dernières 24h pour voir si la connexion marche,
    au lieu de tout charger depuis 2000.
    """
    with st.expander("🔍 Backend connectivity status"):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        FROM = yesterday.strftime("%Y-%m-%d %H:%M:%S")
        UNTIL = now.strftime("%Y-%m-%d %H:%M:%S")
        
        st.caption(f"Testing connection on small window: {FROM} -> {UNTIL}")

        try:
            # On appelle sans cache ici pour tester la vraie connexion
            df_s = get_state_times(FROM, UNTIL)
            st.success(f"✅ State Times: {len(df_s) if df_s is not None else 0} rows retrieved")
        except Exception as e:
            st.error(f"❌ State Times failed: {e}")

        try:
            df_e = get_energy_consumption(FROM, UNTIL)
            st.success(f"✅ Energy: {len(df_e) if df_e is not None else 0} rows retrieved")
        except Exception as e:
            st.error(f"❌ Energy failed: {e}")

def render_home() -> None:
    st.title("🏠 CNC Monitoring Overview")
    st.markdown(f"**Period:** {DEFAULT_START_DATE} to {DEFAULT_END_DATE}")

    # Chargement par défaut sur la période courte (7 jours)
    from_str = to_backend_datetime_str(DEFAULT_START_DATE, start_of_day=True)
    until_str = to_backend_datetime_str(DEFAULT_END_DATE, start_of_day=False)

    # Chargement parallèle (si le backend le permet, sinon séquentiel)
    with st.spinner("Loading dashboard data..."):
        df_states = load_state_times(from_str, until_str)
        df_energy = load_energy(from_str, until_str)
        df_alarms = load_alarms(from_str, until_str)

    state_kpis = compute_state_kpis(df_states)

    # --- KPIs ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Time (h)", f"{state_kpis['total_hours']:.1f}")
    with c2: st.metric("Active Time (h)", f"{state_kpis['active_hours']:.1f}")
    with c3: st.metric("Idle / Off (h)", f"{state_kpis['idle_hours']:.1f}")
    with c4: st.metric("Availability (%)", f"{state_kpis['availability_pct']:.1f}")

    st.markdown("---")

    # --- GRAPHS ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("State Breakdown")
        if df_states.empty:
            st.info("No state data.")
        elif "state" in df_states.columns and "total_hours" in df_states.columns:
            chart_df = df_states.groupby("state")["total_hours"].sum()
            st.bar_chart(chart_df)
            
    with col_g2:
        st.subheader("Energy Trend")
        if df_energy.empty:
            st.info("No energy data.")
        elif "date" in df_energy.columns and "total_energy_kwh" in df_energy.columns:
            chart_df = df_energy.set_index("date")["total_energy_kwh"]
            st.line_chart(chart_df)

    st.markdown("---")
    
    # --- ALARMS SUMMARY ---
    st.subheader("Recent Alarms")
    if df_alarms.empty:
        st.info("No alarms.")
    else:
        st.dataframe(df_alarms.head(10), use_container_width=True) # Affiche juste les 10 dernières

    st.markdown("---")
    render_backend_debug()

def render_operation_monitoring() -> None:
    st.title("⚙️ Operation Monitoring")
    
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("Start", value=DEFAULT_START_DATE, key="op_start")
    with c2:
        end_date = st.date_input("End", value=DEFAULT_END_DATE, key="op_end")

    if start_date > end_date:
        st.error("Error: Start > End")
        return

    from_str = to_backend_datetime_str(start_date, True)
    until_str = to_backend_datetime_str(end_date, False)

    df_states = load_state_times(from_str, until_str)
    
    if df_states.empty:
        st.warning("No data found.")
        return

    kpis = compute_state_kpis(df_states)
    
    # KPIs Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total (h)", f"{kpis['total_hours']:.1f}")
    c2.metric("Active (h)", f"{kpis['active_hours']:.1f}")
    c3.metric("Idle (h)", f"{kpis['idle_hours']:.1f}")
    c4.metric("Avail (%)", f"{kpis['availability_pct']:.1f}")

    st.bar_chart(df_states.set_index("state")["total_hours"])
    st.dataframe(df_states, use_container_width=True)

def render_energy_monitoring() -> None:
    st.title("🔌 Energy Monitoring")
    
    c1, c2 = st.columns(2)
    with c1: start_date = st.date_input("Start", value=DEFAULT_START_DATE, key="en_start")
    with c2: end_date = st.date_input("End", value=DEFAULT_END_DATE, key="en_end")

    if start_date > end_date:
        st.error("Error: Start > End")
        return

    from_str = to_backend_datetime_str(start_date, True)
    until_str = to_backend_datetime_str(end_date, False)
    
    df_energy = load_energy(from_str, until_str)
    
    if df_energy.empty:
        st.warning("No data.")
        return

    total = df_energy["total_energy_kwh"].sum() if "total_energy_kwh" in df_energy.columns else 0
    c1, c2 = st.columns(2)
    c1.metric("Total kWh", f"{total:.1f}")
    
    if "date" in df_energy.columns:
        st.line_chart(df_energy.set_index("date")["total_energy_kwh"])
    
    st.dataframe(df_energy, use_container_width=True)

def render_alarm_monitoring() -> None:
    st.title("🚨 Alarm Monitoring")
    
    c1, c2 = st.columns(2)
    with c1: start_date = st.date_input("Start", value=DEFAULT_START_DATE, key="al_start")
    with c2: end_date = st.date_input("End", value=DEFAULT_END_DATE, key="al_end")

    if start_date > end_date:
        st.error("Error: Start > End")
        return

    from_str = to_backend_datetime_str(start_date, True)
    until_str = to_backend_datetime_str(end_date, False)
    
    df_alarms = load_alarms(from_str, until_str)
    
    if df_alarms.empty:
        st.warning("No alarms.")
        return

    st.metric("Total Events", len(df_alarms))
    
    if "alarm_code" in df_alarms.columns:
        st.bar_chart(df_alarms["alarm_code"].value_counts())

    st.dataframe(df_alarms, use_container_width=True)

# ----------------------------------
# 7. NAVIGATION
# ----------------------------------
st.sidebar.title("CNC Dashboard")
page = st.sidebar.radio("Go to", ["Home", "Operation", "Energy", "Alarms"])

if page == "Home": render_home()
elif page == "Operation": render_operation_monitoring()
elif page == "Energy": render_energy_monitoring()
elif page == "Alarms": render_alarm_monitoring()