WITH base AS (
  SELECT
    to_timestamp(f.date / 1000.0) AS ts,
    f.id_var,
    CASE
      WHEN f.id_var = 550 THEN f.value / 1000.0  -- remise à l’échelle du RPM
      ELSE f.value
    END AS value
  FROM public.variable_log_float f
  WHERE f.id_var IN (537, 498, 620, 565, 550, 544)
    AND to_timestamp(f.date / 1000.0)
        BETWEEN '2020-12-28 06:00:00' AND '2020-12-28 18:00:00'
),

-- 1️⃣ Liste des timestamps observés
all_ts AS (
  SELECT DISTINCT ts FROM base
),

-- 2️⃣ Comblement (Last Observation Carried Forward)
filled AS (
  SELECT
    ts,
    (SELECT value FROM base b WHERE b.id_var = 537 AND b.ts <= a.ts ORDER BY b.ts DESC LIMIT 1) AS x_motor,
    (SELECT value FROM base b WHERE b.id_var = 498 AND b.ts <= a.ts ORDER BY b.ts DESC LIMIT 1) AS y_motor,
    (SELECT value FROM base b WHERE b.id_var = 620 AND b.ts <= a.ts ORDER BY b.ts DESC LIMIT 1) AS z_motor,
    (SELECT value FROM base b WHERE b.id_var = 565 AND b.ts <= a.ts ORDER BY b.ts DESC LIMIT 1) AS eje5_motor,
    (SELECT value FROM base b WHERE b.id_var = 550 AND b.ts <= a.ts ORDER BY b.ts DESC LIMIT 1) AS spindle_rpm,
    (SELECT value FROM base b WHERE b.id_var = 544 AND b.ts <= a.ts ORDER BY b.ts DESC LIMIT 1) AS spindle_load
  FROM all_ts a
),

-- 3️⃣ Normalisation (0-1)
norm_stats AS (
  SELECT
    'x_motor' AS var, MIN(x_motor) AS vmin, MAX(x_motor) AS vmax FROM filled
  UNION ALL SELECT 'y_motor', MIN(y_motor), MAX(y_motor) FROM filled
  UNION ALL SELECT 'z_motor', MIN(z_motor), MAX(z_motor) FROM filled
  UNION ALL SELECT 'eje5_motor', MIN(eje5_motor), MAX(eje5_motor) FROM filled
  UNION ALL SELECT 'spindle_rpm', MIN(spindle_rpm), MAX(spindle_rpm) FROM filled
  UNION ALL SELECT 'spindle_load', MIN(spindle_load), MAX(spindle_load) FROM filled
),
normalized AS (
  SELECT
    ts,
    (x_motor - (SELECT vmin FROM norm_stats WHERE var='x_motor')) / NULLIF((SELECT vmax - vmin FROM norm_stats WHERE var='x_motor'),0) AS x_norm,
    (y_motor - (SELECT vmin FROM norm_stats WHERE var='y_motor')) / NULLIF((SELECT vmax - vmin FROM norm_stats WHERE var='y_motor'),0) AS y_norm,
    (z_motor - (SELECT vmin FROM norm_stats WHERE var='z_motor')) / NULLIF((SELECT vmax - vmin FROM norm_stats WHERE var='z_motor'),0) AS z_norm,
    (eje5_motor - (SELECT vmin FROM norm_stats WHERE var='eje5_motor')) / NULLIF((SELECT vmax - vmin FROM norm_stats WHERE var='eje5_motor'),0) AS eje5_norm,
    (spindle_rpm - (SELECT vmin FROM norm_stats WHERE var='spindle_rpm')) / NULLIF((SELECT vmax - vmin FROM norm_stats WHERE var='spindle_rpm'),0) AS rpm_norm,
    (spindle_load - (SELECT vmin FROM norm_stats WHERE var='spindle_load')) / NULLIF((SELECT vmax - vmin FROM norm_stats WHERE var='spindle_load'),0) AS load_norm
  FROM filled
),

-- 4️⃣ Score pondéré (importance par capteur)
score_series AS (
  SELECT
    ts,
    0.5 * rpm_norm +     -- RPM : influence dominante
    0.3 * load_norm +    -- charge mécanique importante
    0.05 * x_norm +
    0.05 * y_norm +
    0.05 * z_norm +
    0.05 * eje5_norm AS score
  FROM normalized
),

-- 5️⃣ Seuil dynamique lissé (EMA très stable)
dyn_threshold AS (
  SELECT
    ts,
    score,
    0.95 * AVG(score) OVER (ORDER BY ts ROWS BETWEEN 120 PRECEDING AND CURRENT ROW)
      + 0.05 * score AS smoothed_threshold
  FROM score_series
),

-- 6️⃣ État machine (WORKING / IDLE) avec tolérance
state_series AS (
  SELECT
    ts,
    score,
    smoothed_threshold,
    CASE WHEN score > smoothed_threshold * 0.95 THEN 'WORKING' ELSE 'IDLE' END AS machine_state
  FROM dyn_threshold
),

-- 7️⃣ Détection des changements d’état
state_change AS (
  SELECT
    ts,
    machine_state,
    CASE WHEN lag(machine_state) OVER (ORDER BY ts) = machine_state THEN 0 ELSE 1 END AS is_new_group
  FROM state_series
),

-- 8️⃣ Numérotation des groupes continus
grouped AS (
  SELECT
    ts,
    machine_state,
    SUM(is_new_group) OVER (ORDER BY ts) AS grp
  FROM state_change
),

-- 9️⃣ Segments bruts (avant fusion)
segments AS (
  SELECT
    MIN(ts) AS start_time,
    MAX(ts) AS end_time,
    machine_state,
    MAX(ts) - MIN(ts) AS duration
  FROM grouped
  GROUP BY machine_state, grp
),

-- 🔟 Fusion des segments consécutifs identiques
merged_step1 AS (
  SELECT
    *,
    CASE
      WHEN machine_state = LAG(machine_state) OVER (ORDER BY start_time)
      THEN 0 ELSE 1 END AS new_block
  FROM segments
),
merged AS (
  SELECT
    machine_state,
    MIN(start_time) AS start_time,
    MAX(end_time)   AS end_time,
    make_interval(secs => SUM(EXTRACT(EPOCH FROM duration))) AS duration
  FROM (
    SELECT *,
           SUM(new_block) OVER (ORDER BY start_time) AS grp
    FROM merged_step1
  ) t
  GROUP BY grp, machine_state
),

-- 11️⃣ Suppression des micro-segments isolés (<5s)
cleaned AS (
  SELECT
    start_time, end_time, machine_state, duration,
    LAG(machine_state) OVER (ORDER BY start_time)  AS prev_state,
    LEAD(machine_state) OVER (ORDER BY start_time) AS next_state
  FROM merged
),
filtered AS (
  SELECT *
  FROM cleaned
  WHERE NOT (
    EXTRACT(EPOCH FROM duration) < 5
    AND prev_state = next_state
  )
),

-- 12️⃣ Fusion finale (évite WORKING/WORKING, IDLE/IDLE)
final_merge_step1 AS (
  SELECT
    *,
    CASE
      WHEN machine_state = LAG(machine_state) OVER (ORDER BY start_time) THEN 0
      ELSE 1
    END AS new_block2
  FROM filtered
),
final_merge AS (
  SELECT
    machine_state,
    MIN(start_time) AS start_time,
    MAX(end_time)   AS end_time,
    make_interval(secs => SUM(EXTRACT(EPOCH FROM duration))) AS duration
  FROM (
    SELECT *,
           SUM(new_block2) OVER (ORDER BY start_time) AS grp2
    FROM final_merge_step1
  ) t
  GROUP BY grp2, machine_state
)

-- ✅ Résultat final
SELECT
  start_time, end_time, machine_state, duration
FROM final_merge
ORDER BY start_time;
