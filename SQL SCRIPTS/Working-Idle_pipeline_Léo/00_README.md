# Working / Idle Machine State Detection – Léo

This folder contains **Léo’s full approach** to identifying machine WORKING and IDLE states using SQL.
It implements a **weighted sensor scoring system** and a **dynamic EMA-based threshold** to detect true machine activity.

---

## 📂 Folder contents

| File | Description |
|------|--------------|
| `01_variable_selection.sql` | Selects key variables (RPM, Load, axes) from the main float log |
| `02_weighted_score_ema.sql` | Computes the weighted activity score and EMA dynamic threshold |
| `03_state_detection_and_fusion.sql` | Detects WORKING/IDLE states and merges consecutive or micro segments |
| `04_results_summary.sql` | Aggregates results into total working and idle durations |
| `final_pipeline_Léo.sql` | Complete, ready-to-run SQL script combining all steps |

---

## 🧠 Key ideas

- **Weighted scoring**: RPM and Load have the highest impact; axes have smaller weights.
- **Dynamic threshold (EMA)**: automatically adapts to sensor trends using a smoothed window.
- **Segment post-processing**: merges consecutive identical states and removes short transitions (<5s).
- **Result**: realistic detection of continuous working periods, minimizing false idle transitions.

---

## ⚙️ Technologies
- Database: PostgreSQL  
- Data source: `public.variable_log_float`  
- Time window used for tests: `2020-12-28 06:00:00` to `2020-12-28 18:00:00`

---

## 📊 Example outputs

| Machine State | Duration (example) |
|----------------|--------------------|
| WORKING | 13:45:12 |
| IDLE | 02:15:48 |

