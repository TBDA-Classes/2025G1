import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta

# ----------------------------------
# 1. IMPORT BACKEND
# ----------------------------------
try:
    from data_service import (
        get_state_times,
        get_machine_alarms,
        get_energy_consumption,
    )
except ImportError:
    st.error("⛔ Module 'data_service' manquant. Assurez-vous que le fichier est présent.")
    st.stop()

# ----------------------------------
# 2. CONFIGURATION & STYLE
# ----------------------------------
st.set_page_config(page_title="CNC Master Dashboard", layout="wide")

# CSS "Pro" (basé sur votre préférence)
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    /* Style cartes métriques */
    div[data-testid="stMetric"] {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----------------------------------
# 3. NETTOYAGE & CHARGEMENT
# ----------------------------------
def clean_dataframe(df):
    """Nettoyage robuste pour standardiser les colonnes."""
    if df.empty: return df
    
    # Tout en minuscule et sans espaces
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Mapping des noms de colonnes
    rename_map = {
        'etat': 'state', 'status': 'state', 'm_state': 'state',
        'hours': 'total_hours', 'duree': 'total_hours', 'duration': 'total_hours', 'total_hours': 'total_hours',
        'kwh': 'total_energy_kwh', 'energy': 'total_energy_kwh', 'total_kwh': 'total_energy_kwh',
        'code': 'alarm_code', 'alarm': 'alarm_code',
        'timestamp': 'date', 'start_time': 'date', 'time': 'date',
        'desc': 'description', 'message': 'description'
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    
    # Conversion Date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    return df

@st.cache_data(show_spinner=False)
def load_data(start, end):
    # Formatage string pour le backend
    s_str = f"{start} 00:00:00"
    e_str = f"{end} 23:59:59"
    
    try:
        df_s = get_state_times(s_str, e_str)
        df_e = get_energy_consumption(s_str, e_str)
        df_a = get_machine_alarms(s_str, e_str)
        return clean_dataframe(df_s), clean_dataframe(df_e), clean_dataframe(df_a)
    except Exception as e:
        st.error(f"Erreur Backend: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# ----------------------------------
# 4. LOGIQUE MÉTIER (KPIs & Sévérité)
# ----------------------------------
def compute_state_kpis(df_states):
    defaults = {"total_hours": 0.0, "active_hours": 0.0, "idle_hours": 0.0, "availability_pct": 0.0}
    if df_states.empty or "total_hours" not in df_states.columns:
        return defaults

    total_hours = float(df_states["total_hours"].sum())
    
    # Définition de l'activité
    active_states = ["RUN", "ACTIVE", "AUTO", "PRODUCTION", "WORKING", "HIGH ACTIVITY", "LOW ACTIVITY"]
    
    if "state" in df_states.columns:
        is_active = df_states["state"].astype(str).str.upper().isin(active_states)
        active_hours = float(df_states.loc[is_active, "total_hours"].sum())
    else:
        active_hours = 0.0

    idle_hours = total_hours - active_hours
    availability_pct = (active_hours / total_hours * 100.0) if total_hours > 0 else 0.0
    
    return {
        "total_hours": total_hours,
        "active_hours": active_hours,
        "idle_hours": idle_hours,
        "availability_pct": availability_pct,
    }

def infer_severity(row):
    """Déduit la sévérité de l'alarme."""
    text = str(row.get('alarm_code', '')) + " " + str(row.get('description', ''))
    text = text.upper()
    if any(x in text for x in ['ERR', 'CRIT', 'STOP', 'EMERGENCY', 'FAIL', 'FATAL']):
        return 'CRITICAL'
    elif any(x in text for x in ['WARN', 'WRN', 'LOW', 'HIGH', 'TEMP', 'MAINT']):
        return 'WARNING'
    else:
        return 'INFO'

# ----------------------------------
# 5. GRAPHIQUES (ALTAIR)
# ----------------------------------
def make_activity_chart(df):
    """Graphique barres simple."""
    return alt.Chart(df).mark_bar().encode(
        x=alt.X('total_hours', title='Total Heures'),
        y=alt.Y('state', title='État', sort='-x'),
        tooltip=['state', 'total_hours']
    ).interactive()

def make_timeline_chart(df):
    """Timeline (Gantt) pour le zoom journalier."""
    df_plot = df.copy()
    if 'total_hours' in df_plot.columns:
        df_plot['vis_hours'] = df_plot['total_hours'].clip(lower=0.02) # Min visible
        df_plot['end_time'] = df_plot['date'] + pd.to_timedelta(df_plot['vis_hours'], unit='h')
        
        return alt.Chart(df_plot).mark_bar().encode(
            x=alt.X('date:T', title='Heure', axis=alt.Axis(format='%H:%M')),
            x2='end_time:T',
            y=alt.Y('state', title=None),
            color=alt.Color('state', legend=alt.Legend(title="État")),
            tooltip=['date', 'state', 'total_hours']
        ).properties(height=200).interactive()
    return alt.Chart(df).mark_bar() # Vide si erreur

# ----------------------------------
# 6. PAGES
# ----------------------------------

def render_home(df_s, df_a):
    st.title("🏠 CNC Monitoring Overview")
    
    kpis = compute_state_kpis(df_s)
    
    # KPI Globaux
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Time (h)", f"{kpis['total_hours']:.1f}")
    c2.metric("Active Time (h)", f"{kpis['active_hours']:.1f}")
    c3.metric("Idle Time (h)", f"{kpis['idle_hours']:.1f}")
    c4.metric("Availability (%)", f"{kpis['availability_pct']:.1f}")

    st.markdown("---")

    # Graphique FILTRÉ (Pas de Prod, Pas d'Alarme)
    st.subheader("Distribution des Arrêts (Hors Production)")
    
    excluded = ['RUN', 'PRODUCTION', 'ACTIVE', 'ALARM', 'ALARME', 'WORKING', 'AUTO']
    
    if not df_s.empty and 'state' in df_s.columns:
        mask = ~df_s['state'].astype(str).str.upper().isin(excluded)
        df_filtered = df_s[mask]
        
        if not df_filtered.empty:
            # On agrège pour le graphique simple
            df_chart = df_filtered.groupby('state')['total_hours'].sum().reset_index()
            st.altair_chart(make_activity_chart(df_chart), use_container_width=True)
        else:
            st.info("La machine a été 100% productive ou en alarme (Rien d'autre à afficher).")

def render_operation_monitoring(df_s, start_global, end_global):
    st.title("⚙️ Operation Monitoring")
    
    if df_s.empty:
        st.warning("No data found.")
        return

    # --- PARTIE 1 : VUE GLOBALE FILTRÉE ---
    excluded = ['RUN', 'PRODUCTION', 'ACTIVE', 'ALARM', 'ALARME', 'WORKING', 'AUTO']
    if 'state' in df_s.columns:
        mask = ~df_s['state'].astype(str).str.upper().isin(excluded)
        df_filtered = df_s[mask]
    else:
        df_filtered = pd.DataFrame()

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("1. Total Temps Morts")
        if not df_filtered.empty:
            df_grouped = df_filtered.groupby('state')['total_hours'].sum().reset_index()
            st.altair_chart(make_activity_chart(df_grouped), use_container_width=True)
            st.dataframe(df_grouped, hide_index=True, use_container_width=True)
        else:
            st.info("Aucun temps mort.")

    with col_g2:
        st.subheader("2. Évolution Journalière")
        if not df_filtered.empty and 'date' in df_filtered.columns:
            df_filtered['jour'] = df_filtered['date'].dt.date
            df_pivot = df_filtered.pivot_table(index='jour', columns='state', values='total_hours', aggfunc='sum').fillna(0)
            st.bar_chart(df_pivot)

    st.markdown("---")

    # --- PARTIE 2 : ZOOM JOURNALIER ---
    st.subheader("3. Zoom Détail Journée")
    
    c_sel, c_view = st.columns([1, 2])
    with c_sel:
        # Date par défaut intelligente
        def_date = end_global
        if 'date' in df_s.columns and not df_s.empty:
             max_d = df_s['date'].max().date()
             if start_global <= max_d <= end_global: def_date = max_d

        day_selected = st.date_input("Choisir une journée :", value=def_date, min_value=start_global, max_value=end_global)
    
    if 'date' in df_s.columns:
        mask_day = df_s['date'].dt.date == day_selected
        df_day = df_s[mask_day]
        
        with c_view:
            if df_day.empty:
                st.warning(f"Aucune donnée le {day_selected}.")
            else:
                st.write(f"**Chronologie du {day_selected}**")
                st.altair_chart(make_timeline_chart(df_day), use_container_width=True)
                
                # Tableau Détail
                summary = df_day.groupby('state')['total_hours'].sum().reset_index().sort_values('total_hours', ascending=False)
                st.dataframe(summary, hide_index=True, use_container_width=True)

def render_energy_monitoring(df_e):
    st.title("🔌 Energy Monitoring")
    if df_e.empty: 
        st.warning("No energy data.")
        return

    total = df_e["total_energy_kwh"].sum() if "total_energy_kwh" in df_e.columns else 0
    st.metric("Total Period (kWh)", f"{total:.1f}")
    
    if "date" in df_e.columns:
        chart = alt.Chart(df_e).mark_bar().encode(
            x=alt.X('date:T', axis=alt.Axis(format='%d-%b')),
            y=alt.Y('total_energy_kwh', title='kWh'),
            tooltip=['date', 'total_energy_kwh']
        ).interactive()
        st.altair_chart(chart, use_container_width=True)

def render_alarm_monitoring(df_a):
    st.title("🚨 Alarm Monitoring")
    if df_a.empty:
        st.warning("No alarms found.")
        return

    # Logique Sévérité
    df_a['severity'] = df_a.apply(infer_severity, axis=1)
    
    df_crit = df_a[df_a['severity'] == 'CRITICAL']
    df_warn = df_a[df_a['severity'] == 'WARNING']
    df_info = df_a[df_a['severity'] == 'INFO']

    # Métriques
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 Critiques", len(df_crit))
    c2.metric("🟠 Avertissements", len(df_warn))
    c3.metric("🔵 Infos", len(df_info))
    
    st.markdown("---")

    # Onglets
    tab_crit, tab_warn, tab_info, tab_stats = st.tabs(["🔴 Critiques", "🟠 Avertissements", "🔵 Infos", "📊 Stats"])
    
    # Config Colonnes
    cols = [c for c in ['date', 'alarm_code', 'description', 'duration_minutes'] if c in df_a.columns]
    col_cfg = {
        "date": st.column_config.DatetimeColumn("Date", format="D MMM YYYY, HH:mm"),
        "description": st.column_config.TextColumn("Description", width="large")
    }

    with tab_crit:
        if not df_crit.empty: st.dataframe(df_crit[cols], hide_index=True, use_container_width=True, column_config=col_cfg)
        else: st.success("Rien à signaler.")
    with tab_warn:
        if not df_warn.empty: st.dataframe(df_warn[cols], hide_index=True, use_container_width=True, column_config=col_cfg)
        else: st.success("Rien à signaler.")
    with tab_info:
        if not df_info.empty: st.dataframe(df_info[cols], hide_index=True, use_container_width=True, column_config=col_cfg)
        else: st.info("Vide.")
    with tab_stats:
        if 'alarm_code' in df_a.columns:
            st.bar_chart(df_a['alarm_code'].value_counts().head(10))

# ----------------------------------
# 7. MAIN NAVIGATION
# ----------------------------------
st.sidebar.title("CNC Dashboard")

# Bornes Dates
DATA_MIN = date(2020, 12, 28)
DATA_MAX = date(2022, 2, 23)

st.sidebar.header("📅 Période")
default_start = DATA_MAX - timedelta(days=7)
dates = st.sidebar.date_input("Sélection", (default_start, DATA_MAX), min_value=DATA_MIN, max_value=DATA_MAX)

if isinstance(dates, tuple) and len(dates) == 2:
    s, e = dates
else:
    s, e = default_start, DATA_MAX

# Chargement
df_states, df_energy, df_alarms = load_data(s, e)

# Navigation
page = st.sidebar.radio("Go to", ["Home", "Operation", "Energy", "Alarms"])

if page == "Home": render_home(df_states, df_alarms)
elif page == "Operation": render_operation_monitoring(df_states, s, e)
elif page == "Energy": render_energy_monitoring(df_energy)
elif page == "Alarms": render_alarm_monitoring(df_alarms)