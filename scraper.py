import pandas as pd
import requests
import json
import sys

url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot with a Session...")
    requests.packages.urllib3.disable_warnings()
    
    # Create a 'Session' to hold cookies
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    try:
        # Step 1: Visit the page to get the session cookie
        print("Visiting site to get hall pass...")
        session.get("https://mscrimestats.dps.ms.gov/tops", verify=False)
        
        # Step 2: Now visit the report link with the cookie in hand
        print("Requesting report data...")
        response = session.get(url, verify=False, timeout=30)
        
        # Step 3: Try to find the data
        tables = pd.read_html(response.text)
        
        # Grab the biggest table (usually the data)
        df = max(tables, key=len)
        
        # Clean up and save
        data = df.dropna(how='all').fillna(0).to_dict(orient='records')
        
        with open('crime_stats_2025.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Success! Captured {len(data)} rows.")

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
