import pandas as pd
import requests
import json

# 1. The URL you found
url = "https://mscrimestats.dps.ms.gov/public/View/dispview.aspx?ReportId=167&MemberSelection_[Incident%20Date].[Incident%20Date%20Hierarchy]=2026"

def run_scraper():
    # 2. Tell the website we are a normal browser
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    # 3. Find the tables on the page
    tables = pd.read_html(response.text)
    
    # 4. Grab the main data table (usually the largest one)
    df = tables[0] 
    
    # 5. Save it as a JSON file for your app
    df.to_json('crime_stats_2026.json', orient='records')
    print("Data updated successfully!")

if __name__ == "__main__":
    run_scraper()
