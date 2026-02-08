import pandas as pd
import requests
import json
import sys
from io import StringIO

url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot: Surgical Stitching...")
    requests.packages.urllib3.disable_warnings()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        # Wrap the text in StringIO to fix that 'FutureWarning' you saw
        all_tables = pd.read_html(StringIO(response.text))
        
        # Filter for only the substantial tables (more than 10 rows)
        big_tables = [t for t in all_tables if len(t) > 10]
        
        if len(big_tables) >= 2:
            # In Beyond 20/20: 
            # big_tables[0] is usually the list of Names
            # big_tables[1] is usually the grid of Numbers
            names_df = big_tables[0]
            values_df = big_tables[1]
            
            combined_data = []
            for idx in range(len(names_df)):
                name = str(names_df.iloc[idx, 0])
                
                # Clean up junk names
                if name.lower() in ["jurisdiction", "total", "nan", "measures"]:
                    continue
                
                # Create the record
                row_data = {"Agency": name}
                
                # Get the numbers from the matching row in the values table
                # We use idx-1 or idx depending on how the headers aligned
                try:
                    numbers = values_df.iloc[idx].tolist()
                    row_data["Total Crimes"] = int(numbers[0]) if pd.notnull(numbers[0]) else 0
                    row_data["Violent Crime"] = int(numbers[1]) if pd.notnull(numbers[1]) else 0
                except:
                    continue
                    
                combined_data.append(row_data)

            with open('crime_stats_2025.json', 'w') as f:
                json.dump(combined_data, f, indent=4)
            
            print(f"Success! Captured {len(combined_data)} agencies.")
        else:
            print(f"Found {len(big_tables)} big tables, need at least 2.")
            sys.exit(1)

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
