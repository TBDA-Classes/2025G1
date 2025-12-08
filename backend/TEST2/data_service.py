import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# 1. CATALOGUE D'ALARMES (Règles Métier)
# ==========================================
# Traduction et classification des alarmes basées sur tes captures d'écran
ALARM_CATALOG = {
    # --- SAFETY & CRITICAL (ROUGE) ---
    "PLC00501": {"severity": "CRITICAL", "category": "SAFETY", "desc": "External Emergency Stop"},
    "230-0005": {"severity": "CRITICAL", "category": "SAFETY", "desc": "External Emergency Stop (Remote)"},
    "PLC01004": {"severity": "CRITICAL", "category": "SAFETY", "desc": "Machine Emergency Button Pressed"},
    "230-00fd": {"severity": "CRITICAL", "category": "AXIS",   "desc": "Limit Switch Hit (Axis Over-travel)"},
    "PLC00532": {"severity": "CRITICAL", "category": "ATC",    "desc": "Tool Magazine Misalignment"},
    "PLC00853": {"severity": "CRITICAL", "category": "ATC",    "desc": "ATC Interruption Error"},

    # --- WARNINGS (ORANGE) ---
    "PLC00010": {"severity": "WARNING",  "category": "DOOR",   "desc": "Door Open"},
    "PLC01005": {"severity": "WARNING",  "category": "DOOR",   "desc": "Enclosure Door Open"},
    "PLC00739": {"severity": "WARNING",  "category": "DOOR",   "desc": "Enclosure Open in Mode 3"},
    "PLC00474": {"severity": "WARNING",  "category": "OPS",    "desc": "Handwheel Required (Door Open)"},
    "PLC00661": {"severity": "WARNING",  "category": "FLUIDS", "desc": "Oil Recovery Tank Full"},
    "PLC00491": {"severity": "WARNING",  "category": "MAINT",  "desc": "Rotary Joint Lubrication Required"},
    "PLC00655": {"severity": "WARNING",  "category": "MAINT",  "desc": "Retighten Tool Clamping Collets"},
    "130-009e": {"severity": "WARNING",  "category": "SYSTEM", "desc": "File Access Impossible"},
    "240-07d2": {"severity": "WARNING",  "category": "SYSTEM", "desc": "Incorrect File Type"},

    # --- INFO (BLEU/GRIS) ---
    "PLC00054": {"severity": "INFO",     "category": "OPS",    "desc": "Feedrate Override at 0%"},
    "PLC00499": {"severity": "INFO",     "category": "OPS",    "desc": "Feed Hold Active"},
    "PLC00051": {"severity": "INFO",     "category": "OPS",    "desc": "M01 Conditional Stop"},
    "PLC00050": {"severity": "INFO",     "category": "OPS",    "desc": "M00 Program Stop"},
    "320-0064": {"severity": "INFO",     "category": "SYSTEM", "desc": "Strobe T Interrupted"},
    "130-019c": {"severity": "INFO",     "category": "SYSTEM", "desc": "Service Files Saved"},
}

UNKNOWN_ALARM = {"severity": "WARNING", "category": "UNKNOWN", "desc": "Unknown Alarm Code"}

# ==========================================
# 2. GÉNÉRATEURS DE DONNÉES (SIMULATION)
# ==========================================

def get_machine_alarms(from_str, until_str):
    """Génère des alarmes réalistes et les enrichit."""
    # Simulation de données brutes
    dates = pd.date_range(start=from_str, end=until_str, periods=15)
    # On prend quelques codes au hasard dans notre catalogue
    keys = list(ALARM_CATALOG.keys())
    
    data = []
    for d in dates:
        code = np.random.choice(keys)
        # On ajoute un peu de hasard pour simuler des 'trous'
        if np.random.random() > 0.3:
            data.append({"timestamp": d, "alarm_code": code})
            
    df = pd.DataFrame(data)
    
    if df.empty:
        return pd.DataFrame()

    # ENRICHISSEMENT (Mapping)
    def lookup(code):
        return ALARM_CATALOG.get(str(code), UNKNOWN_ALARM)

    enriched = df["alarm_code"].apply(lookup).apply(pd.Series)
    df_final = pd.concat([df, enriched], axis=1)
    
    return df_final

def get_state_times(from_str, until_str):
    """Simule des états machine."""
    states = ["PRODUCTION", "True Idle (Off)", "High Activity", "Low Activity", "Intermediate Activity", "ALARM"]
    data = {
        "state": states,
        "total_hours": [np.random.uniform(10, 50) for _ in states]
    }
    return pd.DataFrame(data)

def get_energy_consumption(from_str, until_str):
    """Simule une conso d'énergie journalière."""
    # Conversion string -> datetime pour pandas
    start = pd.to_datetime(from_str)
    end = pd.to_datetime(until_str)
    
    dates = pd.date_range(start=start, end=end, freq='D')
    energy = np.random.uniform(10, 100, size=len(dates))
    
    # Ajout de pics (spikes)
    if len(energy) > 5:
        energy[2] = 150 # Spike
        energy[4] = 180 # Spike
        
    return pd.DataFrame({"date": dates, "total_energy_kwh": energy})