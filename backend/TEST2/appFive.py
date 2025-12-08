import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, timedelta

# ----------------------------------
# 1. IMPORT BACKEND DATA SERVICES
# ----------------------------------
# Assure-toi que ce fichier existe bien localement
try:
    from data_service import (
        get_state_times,
        get_machine_alarms,
        get_energy_consumption,
    )
except ImportError:
    # Fallback pour éviter le crash si le fichier manque lors du copy-paste
    st.error("Module 'data_service' not found. Please ensure the backend file is present.")
    def get_state_times(*args): return pd.DataFrame()
    def get_machine_alarms(*args): return pd.DataFrame()
    def get_energy_consumption(*args): return pd.DataFrame()

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
# 3. PAGE CONFIG & UI SETUP
# ----------------------------------
st.set_page_config(
    page_title="CNC Monitoring Dashboard",
    layout="wide"
)

# CSS pour cacher le menu hamburger, le footer et le header (Mode Pro)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- A. DEFINITION DES BORNES DE DONNEES ---
DATA_MIN_DATE = date(2020, 12, 28)
DATA_MAX_DATE = date(2022, 2, 23)

# --- B. SELECTEUR GLOBAL DANS LA SIDEBAR ---
st.sidebar.header("📅 Analysis Period")

selected_range = st.sidebar.date_input(
    "Select Date Range",
    value=(DATA_MAX_DATE - timedelta(days=7), DATA_MAX_DATE),
    min_value=DATA_MIN_DATE,
    max_value=DATA_MAX_DATE,
    key="global_date_range"
)

# Sécurisation des dates
if isinstance(selected_range, tuple) and len(selected_range) == 2:
    start_date, end_date = selected_range
elif isinstance(selected_range, tuple) and len(selected_range) == 1:
    start_date = selected_range[0]
    end_date = start_date
else:
    start_date = DATA_MAX_DATE - timedelta(days=7)
    end_date = DATA_MAX_DATE

# --- C. UTILITAIRE DE FORMATAGE ---
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
    
    # --- MODIFICATION ICI ---
    # Liste des mots-clés qui signifient que la machine TRAVAILLE
    # Tout ce qui N'EST PAS dans cette liste sera compté comme Idle/Off.
    active_states = {
        "RUN", "ACTIVE", "AUTO", "PRODUCTION", "WORKING", # Anciens tags (au cas où)
        "HIGH ACTIVITY", 
        "LOW ACTIVITY", 
        "INTERMEDIATE ACTIVITY"
    }
    # ------------------------
    
    # On convertit tout en majuscules (.str.upper()) pour éviter les erreurs de casse
    df_states["is_active"] = df_states[col_state].astype(str).str.upper().isin(active_states)
    
    active_hours = float(df_states.loc[df_states["is_active"], col_hours].sum())
    
    # Le temps Idle est le reste (Total - Actif)
    idle_hours = total_hours - active_hours if total_hours > 0 else 0.0
    
    availability_pct = (active_hours / total_hours * 100.0) if total_hours > 0 else 0.0
    
    return {
        "total_hours": total_hours,
        "active_hours": active_hours,
        "idle_hours": idle_hours,
        "availability_pct": availability_pct,
    }

# ----------------------------------
# 6. HELPER: Custom Altair Charts
# ----------------------------------
def make_energy_chart(df):
    """Crée un graph d'énergie propre avec axe X formatté par jour"""
    return alt.Chart(df).mark_bar(color='#3182bd').encode(
        x=alt.X(
            'date:T', 
            title='Date',
            axis=alt.Axis(format='%d-%b', tickCount='day', labelAngle=-45) # Format explicite Jour-Mois
        ),
        y=alt.Y('total_energy_kwh', title='Energy (kWh)'),
        tooltip=[alt.Tooltip('date', format='%Y-%m-%d', title='Date'), 'total_energy_kwh']
    ).interactive()

def make_activity_chart(df):
    return alt.Chart(df).mark_bar().encode(
        x=alt.X('total_hours', title='Total Hours'),
        y=alt.Y('state', title='State', sort='-x'),
        tooltip=['state', 'total_hours']
    ).interactive()

# ----------------------------------
# 7. PAGES
# ----------------------------------

def render_home() -> None:
    st.title("🏠 CNC Monitoring Overview")
    
    st.markdown(f"**Analysis Period:** {start_date} to {end_date}")

    # Conversion pour le backend
    from_str = to_backend_datetime_str(start_date, start_of_day=True)
    until_str = to_backend_datetime_str(end_date, start_of_day=False)

    with st.spinner("Loading data..."):
        df_states = load_state_times(from_str, until_str)
        df_energy = load_energy(from_str, until_str)
        df_alarms = load_alarms(from_str, until_str)

    state_kpis = compute_state_kpis(df_states)

    # --- KPIs (EN ANGLAIS) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Time (h)", f"{state_kpis['total_hours']:.1f}")
    with c2: st.metric("Active Time (h)", f"{state_kpis['active_hours']:.1f}")
    with c3: st.metric("Idle Time (h)", f"{state_kpis['idle_hours']:.1f}")
    with c4: st.metric("Availability (%)", f"{state_kpis['availability_pct']:.1f}")

    st.markdown("---")

    # --- GRAPHS ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("State Distribution")
        if df_states.empty:
            st.info("No state data for this period.")
        elif "state" in df_states.columns and "total_hours" in df_states.columns:
            # Utilisation d'Altair pour un look plus propre
            chart = make_activity_chart(df_states)
            st.altair_chart(chart, use_container_width=True)
            
    with col_g2:
        st.subheader("Energy Trend")
        if df_energy.empty:
            st.info("No energy data.")
        elif "date" in df_energy.columns and "total_energy_kwh" in df_energy.columns:
            # Utilisation de la fonction helper Altair pour l'axe X corrigé
            chart = make_energy_chart(df_energy)
            st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    
    # --- ALARMS SUMMARY ---
    st.subheader("Latest Alarms")
    if df_alarms.empty:
        st.info("No alarms found.")
    else:
        # HIDE INDEX pour un tableau propre
        st.dataframe(df_alarms.head(10), hide_index=True, use_container_width=True)

    # Note: Backend debug removed from UI as requested

def render_operation_monitoring() -> None:
    st.title("⚙️ Operation Monitoring")
    
    from_str = to_backend_datetime_str(start_date, True)
    until_str = to_backend_datetime_str(end_date, False)

    df_states = load_state_times(from_str, until_str)
    
    if df_states.empty:
        st.warning("No data found for this period.")
        return

    kpis = compute_state_kpis(df_states)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total (h)", f"{kpis['total_hours']:.1f}")
    c2.metric("Active (h)", f"{kpis['active_hours']:.1f}")
    c3.metric("Idle (h)", f"{kpis['idle_hours']:.1f}")
    c4.metric("Avail. (%)", f"{kpis['availability_pct']:.1f}")

    # Graphique Altair
    st.altair_chart(make_activity_chart(df_states), use_container_width=True)
    
    # Tableau sans index
    st.dataframe(df_states, hide_index=True, use_container_width=True)

def render_energy_monitoring() -> None:
    st.title("🔌 Energy Monitoring")
    
    from_str = to_backend_datetime_str(start_date, True)
    until_str = to_backend_datetime_str(end_date, False)
    
    df_energy = load_energy(from_str, until_str)
    
    if df_energy.empty:
        st.warning("No energy data found.")
        return

    total = df_energy["total_energy_kwh"].sum() if "total_energy_kwh" in df_energy.columns else 0
    
    c1, c2 = st.columns(2)
    c1.metric("Total Period (kWh)", f"{total:.1f}")
    
    if "date" in df_energy.columns:
        # Graphique Altair avec Axe X corrigé
        chart = make_energy_chart(df_energy)
        st.altair_chart(chart, use_container_width=True)
    
    st.dataframe(df_energy, hide_index=True, use_container_width=True)

def render_alarm_monitoring() -> None:
    st.title("🚨 Alarm Monitoring")
    
    from_str = to_backend_datetime_str(start_date, True)
    until_str = to_backend_datetime_str(end_date, False)
    
    df_alarms = load_alarms(from_str, until_str)
    
    if df_alarms.empty:
        st.warning("No alarms found.")
        return

    st.metric("Total Events", len(df_alarms))
    
    if "alarm_code" in df_alarms.columns:
        st.bar_chart(df_alarms["alarm_code"].value_counts())

    st.dataframe(df_alarms, hide_index=True, use_container_width=True)

# ----------------------------------
# 8. NAVIGATION
# ----------------------------------
st.sidebar.title("CNC Dashboard")
page = st.sidebar.radio("Go to", ["Home", "Operation", "Energy", "Alarms"])

if page == "Home": render_home()
elif page == "Operation": render_operation_monitoring()
elif page == "Energy": render_energy_monitoring()
elif page == "Alarms": render_alarm_monitoring()