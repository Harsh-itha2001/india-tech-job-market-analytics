import pandas as pd
import numpy as np
import sys
import os
import urllib.parse
from sqlalchemy import create_engine

print("==================================================")
print("WHAT: Complete Mudra ETL & Database Pipeline")
print("WHY: Clean Naukri.com data & automate MySQL Upload")
print("WHERE: Processing locally & loading into local DB")
print("==================================================")

# ==================================================
# STAGE 1: EXTRACT THE DOWNLOADED DATA
# ==================================================
raw_file = "indian_tech_jobs_raw.csv"

# Verify that the raw file exists before running
if not os.path.exists(raw_file):
    print(f"[!] CRITICAL ERROR: '{raw_file}' not found. Run your downloader first!")
    sys.exit()

df = pd.read_csv(raw_file)
print(f"-> Successfully extracted {df.shape[0]} raw records.")


# ==================================================
# STAGE 2: BASELINE STRUCTURAL CLEANING
# ==================================================
df = df.dropna(subset=['title', 'company'])

# --- Clean Locations ---
def clean_location(loc_str):
    if pd.isna(loc_str) or str(loc_str).strip() == '' or str(loc_str).lower() == 'none':
        return "Remote"
    first_city = str(loc_str).split(',')[0].split('/')[0].strip()
    first_city_lower = first_city.lower()
    if "bangalore" in first_city_lower or "bengaluru" in first_city_lower:
        return "Bengaluru"
    if "delhi" in first_city_lower or "ncr" in first_city_lower or "noida" in first_city_lower or "gurgaon" in first_city_lower or "gurugram" in first_city_lower:
        return "NCR-Region"
    if "mumbai" in first_city_lower or "navi mumbai" in first_city_lower:
        return "Mumbai"
    if "hyderabad" in first_city_lower:
        return "Hyderabad"
    if "pune" in first_city_lower:
        return "Pune"
    if "chennai" in first_city_lower:
        return "Chennai"
    return first_city.title()

df['cleaned_location'] = df['location'].apply(clean_location)

# --- Clean Ratings ---
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['rating'] = df['rating'].fillna(3.0)
df.loc[df['rating'] == 0.0, 'rating'] = 3.0


# ==================================================
# STAGE 3: ADVANCED DOMAIN-LEVEL CLEANING
# ==================================================
print("\n--- Running Advanced Quality Checks ---")

# --- Step 1: Detect and Fix Experience Outliers ---
df['min_experience'] = pd.to_numeric(df['min_experience'], errors='coerce')
realistic_median = df[df['min_experience'] < 25]['min_experience'].median()
df.loc[df['min_experience'] >= 25, 'min_experience'] = realistic_median
df['min_experience'] = df['min_experience'].fillna(realistic_median).astype(int)
print(f"-> Outlier Check: Cleaned and normalized minimum experience required columns.")

# --- Step 2: Standardize Job Titles ---
def normalize_job_title(title_str):
    title_lower = str(title_str).lower()
    if "data analyst" in title_lower or "analytics" in title_lower or "analyst" in title_lower:
        return "Data Analyst"
    if "data scientist" in title_lower or "science" in title_lower or "machine learning" in title_lower or "ml" in title_lower:
        return "Data Scientist"
    if "engineer" in title_lower or "developer" in title_lower or "programming" in title_lower:
        return "Software/Data Engineer"
    return "Other Tech Roles"

df['standard_job_title'] = df['title'].apply(normalize_job_title)
print("-> Title Check: Grouped raw titles into standard business roles.")

# --- Step 3: Deduplicate ---
df = df.drop_duplicates(subset=['standard_job_title', 'company', 'cleaned_location'])

# Keep only the target columns that match our SQL table schema exactly
final_df = df[['company', 'standard_job_title', 'cleaned_location', 'rating', 'min_experience']].copy()
print(f"-> Transformation Complete! Prepared {final_df.shape[0]} clean records.")


# ==================================================
# STAGE 4: AUTOMATIC DATABASE LOAD (MySQL)
# ==================================================
print("\n--- Connecting to Local MySQL Database Server ---")

# Setup database parameters
db_user = "root"
db_password = "Admin@123"             # Your MySQL root password
db_host = "localhost"                 # 'localhost' targets your local computer hosting the server
db_port = "3306"
db_name = "india_job_market_db"       # Matches your created MySQL database

try:
    # URL-encode the password to safely escape special characters like '@'
    safe_password = urllib.parse.quote_plus(db_password)
    
    # Build connection URI and create SQLAlchemy Engine
    connection_uri = f"mysql+pymysql://{db_user}:{safe_password}@{db_host}:{db_port}/{db_name}"
    db_engine = create_engine(connection_uri)
    
    print("-> Connected to MySQL Engine successfully.")
    print(f"-> Uploading {final_df.shape[0]} rows to table 'cleaned_job_listings'...")
    
    # Write to local database table
    final_df.to_sql(
        name='cleaned_job_listings', 
        con=db_engine, 
        if_exists='append', 
        index=False
    )
    
    print("\n==================================================")
    print("SUCCESS: India Job Market Pipeline Executed Cleanly!")
    print(f"Database Table 'cleaned_job_listings' is now live with {final_df.shape[0]} rows!")
    print("==================================================")

except Exception as e:
    print("\n[!] DATABASE UPLOAD ERROR:")
    print(e)
    print("\nEnsure your MySQL server is running locally and the table schema has been prepared.")
