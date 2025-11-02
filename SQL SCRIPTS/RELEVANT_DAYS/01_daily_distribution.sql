-- ============================================
-- 01_daily_distribution.sql
-- Purpose: Compute total log counts per day
--          and split days into 10 deciles of activity
-- ============================================

-- Step 1️⃣ Combine both float and string log tables and count total logs per day
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

-- Step 2️⃣ Rank days by activity level using deciles (10 equal-sized groups)
ranked AS (
  SELECT
    day,
    total_count,
    ntile(10) OVER (ORDER BY total_count) AS decile         
  FROM daily
)

-- Step 3️⃣ Compute summary statistics for each decile
SELECT
  decile,
  COUNT(*) AS days_in_bin,                                   
  MIN(total_count) AS min_in_bin,                            
  MAX(total_count) AS max_in_bin,                        
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_count) AS median_in_bin 
FROM ranked
GROUP BY decile
ORDER BY decile;
