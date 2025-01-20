# import pandas , bs4 and requests 
import datetime
import io
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
from PyPDF2 import PdfReader
from dateutil import parser

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

def visitor_body(text, cm, tm, font_dict, font_size, parts):
    y = tm[5]
    if y > 50 and y < 720:
        parts.append(text)

def get_pdfs(link):
    content = req.get(link).content
    document = ''
    title = None
    with io.BytesIO(content) as f:
        pdf = PdfReader(f)
        title = pdf.metadata.title
        # most of the time the content is between the second and 50th page at max
        for page in range(2,50):
            text = pdf.pages[page].extract_text()
            document += text
    return document, title

def clean_pdfs(text, title):
    headerpattern = re.compile(r'\d?\s+Economic Bulletin, issue \d.*?\n')
    month_match = re.search(r'\((\w+ \d{4})\)', title)
    if month_match:
        title = month_match.group(1)
        parsed_date = parser.parse(title)
        formatted_date = parsed_date.strftime("%Y-%m")
        title = formatted_date
    text = re.sub(headerpattern, '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^\d*\s*ECB\s*Economic\s*Bulletin,\s*Issue\s*\d+\s*/\s*\d{4}\s*[–-]\s*Economic\s*and\s*monetary\s*developments', '', text, flags=re.IGNORECASE|re.MULTILINE)    
    text = f'""" + {text} + """'
    return text, title

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
            links[key] = 'https://www.ecb.europa.eu' + value   
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
        if 'pdf' in link:
            text, title = get_pdfs(link)
            text, s = clean_pdfs(text, title)
            reports[date] = text
            continue
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
            report = re.sub(r'\s+', ' ', report)
            reports[date] = report
        except Exception as e:
            print(e)
            continue
    return reports

def save_reports(reports, output = 'reports.csv'):
    df = pd.DataFrame(reports.items(), columns = ['Date', 'Report'])
    df.insert(1, 'Type', 'Monetary Policy Decisions')
    df['Report'] = df['Report'].apply(clean_text)
    df.to_csv(output, index = False, sep=';')

        


def main():
    url = EEB_URL
    url2 = MPD_URL
    start_time = time.time()
    print("Starting EZB scraping process...")

    output_path_mpd = 'data/raw_pdf/ezb/all_reports.csv'
    output_path_ebb = 'data/raw_pdf/ezb/all_bulletins.csv'

    print('initializing selenium ..')
    source = seleniumstarter(url)
    print(f'downloading bullets from {url}')
    bullet_links = get_bullet_links(source)
    reports = download_reports(bullet_links)
    save_reports(reports, output_path_ebb)
    print('initializing selenium ..')
    source = seleniumstarter(url2)
    print(f'downloading reports from {url2}')
    links = get_linkdict(source)
    save_reports(reports, output_path_mpd)


    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    print(f"Downloaded {len(reports)} reports")

if __name__ == '__main__':
    main()