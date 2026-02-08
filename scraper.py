import pandas as pd
import requests
import json
import sys
from io import StringIO

# We are testing with 2025 to make sure we see names and numbers
url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot: The Great Matchmaker...")
    requests.packages.urllib3.disable_warnings()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        all_tables = pd.read_html(StringIO(response.text))
        
        # Step 1: Find the table with the names (it usually has the word 'Jurisdiction')
        names_list = []
        for t in all_tables:
            if t.astype(str).apply(lambda x: x.str.contains('Jurisdiction', case=False)).any().any():
                # Grab the column that has the actual names
                names_list = t.iloc[:, -1].tolist() 
                break

        # Step 2: Find the table with the numbers (the one you found earlier)
        data_table = max(all_tables, key=lambda t: t.shape[1])
        
        # Step 3: Glue them together
        combined_data = []
        for idx, name in enumerate(names_list):
            # Skip the header rows
            if str(name).lower() in ["jurisdiction", "total", "nan", "measures", "0"]:
                continue
            
            try:
                row_numbers = data_table.iloc[idx].tolist()
                combined_data.append({
                    "Agency": str(name),
                    "Total_Crimes": str(row_numbers[0]),
                    "Violent_Crime": str(row_numbers[1]),
                    "Property_Crime": str(row_numbers[2])
                })
            except:
                continue

        if not combined_data:
            print("Failed to match names to numbers.")
            sys.exit(1)

        with open('crime_stats_2025.json', 'w') as f:
            json.dump(combined_data, f, indent=4)
        
        print(f"Success! Matched {len(combined_data)} agencies with their numbers.")

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
