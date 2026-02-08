import pandas as pd
import requests
import json
import sys
from io import StringIO

base_url = "https://mscrimestats.dps.ms.gov/tops/"
report_url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot: Index-Aware Search...")
    requests.packages.urllib3.disable_warnings()
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'})
    
    try:
        session.get(base_url, verify=False, timeout=30)
        response = session.get(report_url, verify=False, timeout=30)
        
        # Read HTML but keep the header structure loose
        all_tables = pd.read_html(StringIO(response.text), header=None)
        
        data_table = None
        for t in all_tables:
            # We look for a table that contains actual text names like "Police" or "Sheriff"
            # AND has multiple columns of numbers
            if t.shape[1] > 3 and t.iloc[:, 0].astype(str).str.contains('Police|Sheriff|County', case=False, na=False).any():
                data_table = t
                break
        
        if data_table is not None:
            cleaned_data = []
            for idx, row in data_table.iterrows():
                # Force the first column to be treated as text
                agency_name = str(row[0])
                
                # Check if this row actually looks like an agency name
                # (It shouldn't be a number like '5545' or 'nan')
                if not agency_name.replace('.', '', 1).isdigit() and "nan" not in agency_name.lower():
                    
                    status = "Reporting"
                    if "Not Reporting" in agency_name:
                        status = "Not Reporting"
                        
                    cleaned_data.append({
                        "Agency": agency_name,
                        "Status": status,
                        # Grab the rest of the columns as the numbers
                        "Stats": row[1:].fillna(0).astype(str).tolist()
                    })

            with open('crime_stats_2025.json', 'w') as f:
                json.dump(cleaned_data, f, indent=4)
            
            print(f"Success! Captured {len(cleaned_data)} agencies with correct names.")
        else:
            print("Could not find a table with Agency Names in the first column.")
            sys.exit(1)

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
