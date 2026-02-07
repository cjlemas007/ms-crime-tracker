import pandas as pd
import requests
import json
import sys

# The URL for 2026 data
url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2026"

def run_scraper():
    print("Starting robot...")
    
    # Mimic a real person using a Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status() # Check if the website actually loaded
        
        # Read the tables from the website
        tables = pd.read_html(response.text)
        
        if not tables:
            print("Error: No data tables found on the page.")
            sys.exit(1)
            
        # Usually the data is in the first or second table
        df = tables[0]
        
        # Convert the table to a list of rows
        data = df.to_dict(orient='records')
        
        # Save to a file
        with open('crime_stats_2026.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        print("Success! Data saved to crime_stats_2026.json")

    except Exception as e:
        print(f"Robot failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_scraper()
