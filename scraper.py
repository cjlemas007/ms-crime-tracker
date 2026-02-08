import pandas as pd
import requests
import json
import sys
from io import StringIO

url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot: Universal Table Grabber...")
    requests.packages.urllib3.disable_warnings()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        all_tables = pd.read_html(StringIO(response.text))
        
        # Find the single biggest table on the page
        df = max(all_tables, key=len)
        print(f"Found data table with {df.shape[0]} rows and {df.shape[1]} columns.")

        combined_data = []
        
        for idx in range(len(df)):
            # Grab the first column as the name
            name = str(df.iloc[idx, 0])
            
            # Skip noise
            if name.lower() in ["jurisdiction", "total", "nan", "measures", "none", "0"]:
                continue
            
            # Build the record using column positions (0, 1, 2) rather than names
            row_data = {
                "Agency": name,
                "Stat_A": str(df.iloc[idx, 1]) if df.shape[1] > 1 else "0",
                "Stat_B": str(df.iloc[idx, 2]) if df.shape[1] > 2 else "0",
                "Stat_C": str(df.iloc[idx, 3]) if df.shape[1] > 3 else "0"
            }
            combined_data.append(row_data)

        if not combined_data:
            print("Captured 0 rows. Table structure might be empty.")
            sys.exit(1)

        with open('crime_stats_2025.json', 'w') as f:
            json.dump(combined_data, f, indent=4)
        
        print(f"Success! Saved {len(combined_data)} agencies to JSON.")

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
