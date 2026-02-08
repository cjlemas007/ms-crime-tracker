import pandas as pd
import requests
import json
import sys

url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2025"

def run_scraper():
    print("Starting robot: Stitching Names and Numbers...")
    requests.packages.urllib3.disable_warnings()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        all_tables = pd.read_html(response.text)

        # Beyond 20/20 puts Names in one table and Numbers in the next
        # We need to find the specific pair that matches
        names_table = None
        values_table = None

        for i in range(len(all_tables)):
            # The Names table usually has 'Jurisdiction' in the first row
            if "Jurisdiction" in str(all_tables[i]):
                names_table = all_tables[i]
                # The Values table is almost always the very next one
                values_table = all_tables[i+1]
                break

        if names_table is not None and values_table is not None:
            # Flatten the tables to simple lists
            names = names_table.iloc[:, 0].tolist()  # Get the first column of names
            
            # Combine them into a single list of dictionaries
            combined_data = []
            for idx, name in enumerate(names):
                # Skip header rows like 'Jurisdiction' or 'Total'
                if name in ["Jurisdiction", "Total", "Measures", "0"]:
                    continue
                
                row_data = {"Agency": str(name)}
                # Add the numbers from the values table for this row
                numbers = values_table.iloc[idx].tolist()
                row_data["Total Crimes"] = numbers[0]
                row_data["Homicide"] = numbers[1]
                row_data["Assault"] = numbers[2]
                
                combined_data.append(row_data)

            with open('crime_stats_2025.json', 'w') as f:
                json.dump(combined_data, f, indent=4)
            
            print(f"Success! Combined {len(combined_data)} agencies with their stats.")
        else:
            print("Could not find the matching Name/Value tables.")
            sys.exit(1)

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
