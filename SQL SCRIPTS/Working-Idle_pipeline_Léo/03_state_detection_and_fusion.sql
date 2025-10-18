-- 03_state_detection_and_fusion.sql
-- Detect WORKING / IDLE states and merge consecutive or micro-segments

WITH dyn_threshold AS (
  SELECT ts, score, smoothed_threshold
  FROM dyn_threshold  -- from previous step
),
state_series AS (
  SELECT
    ts,
    score,
    smoothed_threshold,
    CASE WHEN score > smoothed_threshold * 0.95 THEN 'WORKING' ELSE 'IDLE' END AS machine_state
  FROM dyn_threshold
),
state_change AS (
  SELECT
    ts,
    machine_state,
    CASE WHEN LAG(machine_state) OVER (ORDER BY ts) = machine_state THEN 0 ELSE 1 END AS is_new_group
  FROM state_series
),
grouped AS (
  SELECT ts, machine_state, SUM(is_new_group) OVER (ORDER BY ts) AS grp
  FROM state_change
),
segments AS (
  SELECT
    MIN(ts) AS start_time,
    MAX(ts) AS end_time,
    machine_state,
    MAX(ts) - MIN(ts) AS duration
  FROM grouped
  GROUP BY machine_state, grp
)
SELECT * FROM segments ORDER BY start_time;
