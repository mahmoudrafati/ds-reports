# import pandas , bs4 and requests 
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests as req
import pandas as pd
import time
from tqdm import tqdm 

# Url of the main EZB Monetary Policy page
MPD_URL = 'https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html'
EEB_URL = 'https://www.ecb.europa.eu/press/economic-bulletin/html/all_releases.en.html'

chrome_options = Options()
chrome_options.add_argument("--headless")
BROWSER = webdriver.Chrome(options=chrome_options)

def clean_text(text):
    text_no_newlines = re.sub(r'[\n\r\t]+', ' ', text)
    text= re.sub(r'[\s;]+', ' ', text_no_newlines).strip()

    return text

def seleniumstarter(url, chrome = BROWSER):
    chrome.get(url)
    elem = chrome.find_element(By.TAG_NAME,"html")
    elem.send_keys(Keys.END)
    time.sleep(3)
    elem.send_keys(Keys.HOME)

    source = chrome.page_source
    return source

def get_bullet_links(source):
    soup = BeautifulSoup(source, 'html.parser')
    dl = soup.find('dl')

    links = {}
    for child in dl:
        if child.name == 'dt':
            key = child['isodate']
            value = child.next_sibling.find('div', {'class':'title'}).a['href']
            links[key] = 'https://www.ecb.europa.eu/' + value   
    return links

def get_linkdict(source):
    soup = BeautifulSoup(source, 'html.parser')
    divs = soup.find_all('div', {'class' : 'lazy-load loaded'})
    links = {}

    for div in divs:
        for conts in div.contents:
            if conts == '\n':
                continue
            if conts.name == 'dt':
                key = conts['isodate']
                dd_sibling = conts.next_sibling
                if dd_sibling.name == 'dd' and 'href' in dd_sibling.contents[0].next.attrs.keys():
                    value = dd_sibling.contents[0].next['href']
                links[key] = 'https://www.ecb.europa.eu/' + value
            else:
                continue
    return links

def download_reports(links):
    reports = {}
    for date, link in tqdm(links.items(), desc= "Downloading reports"):
        try:
            res = req.get(link)
            text = res.text
            soup = BeautifulSoup(text, 'html.parser')
            main = soup.main.extract()
            report = ''
            for conts in main:
                try: 
                    if conts.DEFAULT_INTERESTING_STRING_TYPES:
                        if 'class' in conts.attrs and 'section' in conts['class'] :
                            report += conts.text
                except Exception as e:
                    continue
            reports[date] = report
        except Exception as e:
            print(e)
            continue
    return reports


def save_reports(reports, output = 'reports.csv'):
    df = pd.DataFrame(reports.items(), columns = ['Date', 'Report'])
    df.insert(1, 'Type', 'Monetary Policy Decisions')
    df['Report'] = df['Report'].apply(clean_text)
    df.to_csv(output, index = False)

        


def main():
    url = EEB_URL
    start_time = time.time()
    print("Starting EZB scraping process...")

    output_path_mpd = 'data/raw_pdf/ezb/all_reports.csv'
    output_path_ebb = 'data/raw_pdf/ezb/all_bulletins.csv'

    source = seleniumstarter(url)
    bullet_links = get_bullet_links(source)
    #links = get_linkdict(source)
    reports = download_reports(bullet_links)
    save_reports(reports, output_path)


    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    print(f"Downloaded {len(reports)} reports")

if __name__ == '__main__':
    main()
