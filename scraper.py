import pandas as pd
import requests
import json
import sys

# The URL for 2026 data
url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2026"

def run_scraper():
    print("Starting robot...")
    
    # Ignore the SSL certificate error
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        # verify=False is the key fix here
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status() 
        
        tables = pd.read_html(response.text)
        
        if not tables:
            print("Error: No data tables found.")
            sys.exit(1)
            
        df = tables[0]
        data = df.to_dict(orient='records')
        
        with open('crime_stats_2026.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        print("Success! Data saved to crime_stats_2026.json")

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
