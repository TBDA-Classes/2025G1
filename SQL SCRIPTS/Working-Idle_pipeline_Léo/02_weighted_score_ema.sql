-- 02_weighted_score_ema.sql
-- Compute a weighted activity score and apply a smoothed dynamic threshold (EMA-like)

WITH base AS (
  SELECT
    to_timestamp(f.date / 1000.0) AS ts,
    f.id_var,
    CASE WHEN f.id_var = 550 THEN f.value / 1000.0 ELSE f.value END AS value
  FROM public.variable_log_float f
  WHERE f.id_var IN (537, 498, 620, 565, 550, 544)
    AND to_timestamp(f.date / 1000.0)
        BETWEEN '2020-12-28 06:00:00' AND '2020-12-28 18:00:00'
),
score_series AS (
  SELECT
    ts,
    0.5 * MAX(CASE WHEN id_var = 550 THEN value END) +  -- spindle rpm
    0.3 * MAX(CASE WHEN id_var = 544 THEN value END) +  -- spindle load
    0.05 * MAX(CASE WHEN id_var = 537 THEN value END) + -- x motor
    0.05 * MAX(CASE WHEN id_var = 498 THEN value END) + -- y motor
    0.05 * MAX(CASE WHEN id_var = 620 THEN value END) + -- z motor
    0.05 * MAX(CASE WHEN id_var = 565 THEN value END)   -- eje5
    AS score
  FROM base
  GROUP BY ts
),
dyn_threshold AS (
  SELECT
    ts,
    score,
    0.95 * AVG(score) OVER (ORDER BY ts ROWS BETWEEN 120 PRECEDING AND CURRENT ROW)
      + 0.05 * score AS smoothed_threshold
  FROM score_series
)
SELECT * FROM dyn_threshold;
