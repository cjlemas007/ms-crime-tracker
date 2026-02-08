import pandas as pd
import requests
import json
import sys

url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2026"

def run_scraper():
    print("Starting robot...")
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        # This looks for all tables on the page
        all_tables = pd.read_html(response.text)
        
        # We want to find the table that actually contains crime data
        crime_table = None
        for table in all_tables:
            # Check if 'Jurisdiction' or 'Number of Crimes' is in the table columns
            column_text = str(table.columns).lower()
            if 'jurisdiction' in column_text or 'crime' in column_text:
                crime_table = table
                break
        
        if crime_table is None:
            # If we didn't find it by columns, let's try the biggest table on the page
            crime_table = max(all_tables, key=len)

        # Clean up the data: Remove empty rows and "NaN" values
        crime_table = crime_table.dropna(how='all').fillna(0)
        
        # Convert to JSON
        data = crime_table.to_dict(orient='records')
        
        with open('crime_stats_2026.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Success! Captured {len(data)} rows of data.")

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
