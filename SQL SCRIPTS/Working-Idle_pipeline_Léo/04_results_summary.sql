-- 04_results_summary.sql
-- Summarize total time spent in each machine state

WITH segments AS (
  SELECT * FROM final_segments  -- from previous step
)
SELECT
  machine_state,
  SUM(end_time - start_time) AS total_duration
FROM segments
GROUP BY machine_state;
