import pandas as pd
import requests
import json
import sys
from io import StringIO

# 1. The main "Lobby" URL to get a cookie
base_url = "https://mscrimestats.dps.ms.gov/tops/"
# 2. The specific "Room" URL (The Report)
report_url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot with Session Cookies...")
    requests.packages.urllib3.disable_warnings()
    
    # Create a session (this saves cookies automatically)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    })
    
    try:
        # Step 1: Visit the homepage to initialize the session
        print("Visiting homepage to get session ID...")
        session.get(base_url, verify=False, timeout=30)
        
        # Step 2: Now visit the report
        print("Requesting report data...")
        response = session.get(report_url, verify=False, timeout=30)
        
        # Security Check: Did we actually get the report?
        if "Jurisdiction by Geography" not in response.text:
            print("Failed: The robot is stuck on the login or loading page.")
            # Print a small snippet to see what page we actually got
            print(f"Page Title: {response.text[:200]}")
            sys.exit(1)

        # Step 3: Parse the tables
        all_tables = pd.read_html(StringIO(response.text))
        
        # Find the table with the most columns (the data table)
        # The screenshot shows at least 6 columns (Agency + 5 stats)
        data_table = None
        for t in all_tables:
            if t.shape[1] >= 5 and len(t) > 20:
                data_table = t
                break
                
        if data_table is not None:
            # Clean up the data
            # The screenshot shows the agency name is likely in Column 0
            cleaned_data = []
            for idx, row in data_table.iterrows():
                row_list = row.astype(str).tolist()
                agency_name = row_list[0]
                
                # Filter out junk rows
                if agency_name.lower() in ["jurisdiction", "total", "nan"]:
                    continue
                
                # Identify "Non-Reporting" agencies based on the screenshot text
                status = "Reporting"
                if "Not Reporting" in agency_name:
                    status = "Not Reporting"
                
                cleaned_data.append({
                    "Agency": agency_name,
                    "Status": status,
                    "Raw_Data": row_list[1:] # Grab the stats
                })

            with open('crime_stats_2025.json', 'w') as f:
                json.dump(cleaned_data, f, indent=4)
            
            print(f"Success! Captured {len(cleaned_data)} agencies.")
        else:
            print("Could not find the data table in the HTML.")
            sys.exit(1)

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
