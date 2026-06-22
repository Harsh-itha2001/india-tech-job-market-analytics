USE india_job_market_db;

-- ONE SINGLE QUERY TO SHOW ALL KEY STATS IN ONE WINDOW!
SELECT 'Total Uploaded Rows' AS Metric_Name, COUNT(*) AS Metric_Value FROM cleaned_job_listings
UNION ALL
SELECT 'Top Hub (Bengaluru) Jobs Count', COUNT(*) FROM cleaned_job_listings WHERE cleaned_location = 'Bengaluru'
UNION ALL
SELECT 'Total Data Analyst Openings', COUNT(*) FROM cleaned_job_listings WHERE standard_job_title = 'Data Analyst'
UNION ALL
SELECT 'Total Entry-Level (Fresher) Jobs', COUNT(*) FROM cleaned_job_listings WHERE min_experience = 0;