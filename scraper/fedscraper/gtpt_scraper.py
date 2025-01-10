import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

URL = 'https://www.fedsearch.org/fomc-docs/search?advanced_search=true&from_year=1997&search_precision=All+Words&start=0&sort=Most+Recent+First&to_month=1&to_year=2025&number=10&fomc_document_type=minutes&Search=Search&text=&from_month=1'

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

# Funktion zum Scrapen der Links
def scrape_fomc_links(base_url):
    data = {"years": {}}
    while True:
        try:
            response = session.get(base_url, stream=True)
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    # Process the chunk
                    pass
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
        soup = BeautifulSoup(response.content, 'html.parser')
        entries = soup.find_all("p")
        
        if not entries:
            break
        
        num_entries = 0
        for entry in entries:
            link_tag = entry.find("a", href=True)
            if not link_tag:
                continue
            
            link = link_tag['href']
            link = urljoin(base_url, link)  # Convert to absolute URL if relative
            if not (link.endswith(".htm") or link.endswith(".html")):
                continue  # PDF ignorieren
            
            # Datum aus dem Link extrahieren
            date_str = link.split("/")[-1][:8]
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                year = date_obj.strftime("%Y")
                month = date_obj.strftime("%b")
                
                if year not in data["years"]:
                    data["years"][year] = {"links": {}}
                
                data["years"][year]["links"][month] = link
                num_entries += 1
            except ValueError:
                continue  # Überspringe ungültige Datumsangaben
            except ValueError:
                continue  # Überspringe ungültige Datumsangaben
        
        if next_page and num_entries > 0:
            params['start'] += num_entries
        else:
            break
    
    return data

# Daten scrapen und speichern
test = session.get(URL)
#fomc_data = scrape_fomc_links(url)

# Ergebnisse in JSON-Datei speichern
with open("links.json", "w") as json_file:
    json.dump(fomc_data, json_file, indent=4)

print("Links wurden erfolgreich gespeichert in links.json")
