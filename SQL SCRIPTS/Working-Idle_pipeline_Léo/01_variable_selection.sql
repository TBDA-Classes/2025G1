-- 01_variable_selection.sql
-- Select the main float variables to be used in the pipeline

SELECT
    v.id,
    v.name
FROM
    public.variable AS v
WHERE
    v.id IN (537, 498, 620, 565, 550, 544)  -- Axis motors, spindle RPM, spindle load
ORDER BY v.name;
