from datetime import datetime
import time
import os
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm import tqdm

chrome_options = Options()
chrome_options.add_argument("--headless")
BROWSER = webdriver.Chrome(options=chrome_options)

URL = "https://www.ecb.europa.eu/press/pubbydate/html/index.en.html?name_of_publication=Monetary%20policy%20account%7CMonetary%20policy%20statement&year=2025%7C2024%7C2023%7C2022%7C2021%7C2020%7C2019%7C2018%7C2017%7C2016%7C2015%7C2014%7C2013%7C2012%7C2011%7C2010%7C2009%7C2008%7C2007%7C2006%7C2005%7C2004%7C2003%7C2002%7C2001%7C2000%7C1999"
CATEGORY = { 'Monetary Policy Account' : 'MPA',
             'Monetary Policy Statement' : 'MPS',}

# def seleniumstarter(url, chrome = BROWSER):
#     chrome.get(url)
#     elem = chrome.find_element(By.TAG_NAME,"html")
#     elem.send_keys(Keys.END)
#     time.sleep(70)
#     elem.send_keys(Keys.HOME)

#     source = chrome.page_source
#     return source
def seleniumstarter(url, chrome = BROWSER):
    chrome.get(url)
    elem = chrome.find_element(By.TAG_NAME, "html")
    top_height = 3611
    last_height = chrome.execute_script("return document.body.scrollHeight")
    while True:
        elem.send_keys(Keys.END)
        time.sleep(10) 
        new_height = chrome.execute_script("return document.body.scrollHeight")        
        if new_height == last_height:
            break
        last_height = new_height
    source = chrome.page_source
    return source


def get_links(dl):
    links = {}
    for child in tqdm(dl, desc="Getting Links from sourcecode"):
        if child.name == 'dt':
            date_string = child.text
            # Convert string to datetime
            date_object = datetime.strptime(date_string, "%d %B %Y")
            # Format datetime to desired string format
            key = date_object.strftime("%Y-%m-%d")
            if child.next_sibling == '\n':
                sibling = child.next_sibling.next_sibling
            else:
                sibling = child.next_sibling
            if "Press seminar" in sibling.find('div', {'class':'title'}).text:
                continue
            value = sibling.find('div', {'class':'title'}).a['href']
            title_text = sibling.find('div', {'class':'title'}).text
            if title_text.lower() in {k.lower(): v for k, v in CATEGORY.items()}:
                type = {k.lower(): v for k, v in CATEGORY.items()}[title_text.lower()]
            else:
                type = 'REPORT'
            links[key] = {'date': key, 'link': 'https://www.ecb.europa.eu' + value, 'type': type}
    return links 

def get_text(link):
    question_cut = r'We\s+are\s+now\s+at\s+your\s+disposal\s+for\s+questions|We\s+are\s+now\s+ready\s+to\s+take\s+your\s+questions|The\s+members\s+of\s+the\s+Governing\s+Council\s+subsequently\s+finalised\s+the\s+introductory\s+statement|Meeting\s+of\s+the\s+ECB’s\s+Governing\s+Council'
    source = seleniumstarter(link)
    soup = BeautifulSoup(source, 'html.parser')
    text = soup.main.extract().text
    # remove everything after and including the termns in question_cut
    text = re.split(question_cut, text, flags=re.IGNORECASE|re.MULTILINE)[0]
    text = re.sub(r'\s+', ' ', text)
    return text


def main():
    output_dir = 'data/raw_pdf/ezb'
    print('Starting to scrape ECB website')
    source = seleniumstarter(URL)
    soup = BeautifulSoup(source, 'html.parser')
    print('Scraping completed')
    dataloader = soup.find('dl')
    links = get_links(dataloader)
    for date, content in tqdm(links.items(), desc='Transforming texts to csv'):
        text = get_text(content['link'])
        type = content['type']
        df = pd.DataFrame({'Date': date, 'Type': type, 'Text': text}, index=[0])
        year_path = os.path.join(output_dir, date.split('-')[0])
        if not os.path.exists(year_path):
            os.makedirs(year_path)
        df.to_csv(os.path.join(year_path, f'{date}.csv'), index=False, sep=';')






    pass

if __name__ == '__main__':
    main()