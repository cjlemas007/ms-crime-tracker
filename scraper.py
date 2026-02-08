import pandas as pd
import requests
import json
import sys
from io import StringIO
import re

url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot: Brute Force Search...")
    requests.packages.urllib3.disable_warnings()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        # We're going to look for any table that has more than 50 rows (likely the data)
        all_tables = pd.read_html(StringIO(response.text))
        
        target_table = None
        for t in all_tables:
            if len(t) > 50:
                target_table = t
                break
        
        if target_table is not None:
            # Beyond 20/20 often hides names in the first column or column index
            # This script will take everything it finds and clean it
            data = []
            for i, row in target_table.iterrows():
                row_list = row.astype(str).tolist()
                # If the row has a name (like 'Police' or 'Sheriff') and a number
                if any(re.search(r'Police|Sheriff|Hinds|Rankin|Madison', x) for x in row_list):
                    # We found a valid row!
                    name = next(x for x in row_list if re.search(r'Police|Sheriff|Hinds|Rankin|Madison', x))
                    # Find the first thing that looks like a number
                    numbers = [x for x in row_list if re.match(r'^\d+(\.\d+)?$', x)]
                    
                    data.append({
                        "Agency": name.strip(),
                        "Total": numbers[0] if len(numbers) > 0 else "0",
                        "Violent": numbers[1] if len(numbers) > 1 else "0"
                    })

            if data:
                with open('crime_stats_2025.json', 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Success! Found {len(data)} agencies.")
                return

        print("Brute force failed to find a valid data table.")
        sys.exit(1)

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
