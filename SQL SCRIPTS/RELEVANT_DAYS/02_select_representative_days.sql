-- ============================================
-- 02_select_representative_days.sql
-- Purpose: Select one representative day per decile
--          (the day closest to the median activity level)
-- ============================================

-- Step 1️⃣ Recompute daily total logs
WITH daily AS (
  SELECT
    date_trunc('day', to_timestamp(date/1000.0))::date AS day,
    COUNT(*) AS total_count
  FROM (
    SELECT date FROM public.variable_log_float
    UNION ALL
    SELECT date FROM public.variable_log_string
  ) u
  GROUP BY 1
),

-- Step 2️⃣ Assign each day to one of 10 deciles
ranked AS (
  SELECT
    day,
    total_count,
    ntile(10) OVER (ORDER BY total_count) AS decile
  FROM daily
),

-- Step 3️⃣ Compute median total_count per decile
stats AS (
  SELECT
    decile,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_count) AS median_in_bin
  FROM ranked
  GROUP BY decile
),

-- Step 4️⃣ For each decile, find the day whose count is closest to the median
picked AS (
  SELECT
    r.decile,
    r.day,
    r.total_count,
    ABS(r.total_count - s.median_in_bin) AS diff, -- distance from median
    ROW_NUMBER() OVER (PARTITION BY r.decile ORDER BY ABS(r.total_count - s.median_in_bin)) AS rn
  FROM ranked r
  JOIN stats s USING (decile)
)

-- Step 5️⃣ Keep only the single “closest-to-median” day per decile
SELECT
  decile,
  day,
  total_count
FROM picked
WHERE rn = 1
ORDER BY decile;
