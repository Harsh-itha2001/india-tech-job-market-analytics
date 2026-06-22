USE india_job_market_db;

select count(*) AS total_uploaded_rows
from cleaned_job_listings;

select 
    cleaned_location,
    count(*) AS total_jobs,
    round(Avg(rating), 2) AS average_company_rating
from cleaned_job_listings
group by cleaned_location
order by total_jobs DESC;

select 
   standard_job_title,
   count(*) as job_count,
   round((count(*) * 100.0) / (SELECT count(*) from cleaned_job_listings), 2) AS market_percentage
from cleaned_job_listings
group by standard_job_title
order by job_count desc;


select  
    case 
       when min_experience = 0 Then 'Fresher (0 yrs)'
       when min_experience between 1 and 3 then 'Junior (1-3 yrs)'
       when min_experience between 4 and 7 then 'Mid-Level (4-7 yrs)'
       else 'Senior (8+ yrs)'
    end as career_bucket,
    count(*) as total_listings,
    round(avg(rating), 1) as average_company_rating
from cleaned_job_listings
group by career_bucket
order by total_listings desc;
       
