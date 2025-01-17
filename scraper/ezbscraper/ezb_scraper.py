# import pandas , bs4 and requests 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests as req
import pandas as pd
import time 

# Url of the main EZB Monetary Policy page
url = 'https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html'

chrome = webdriver.Chrome()
chrome.get(url)
elem = chrome.find_element(By.TAG_NAME,"html")
elem.send_keys(Keys.END)
time.sleep(3)


elem.send_keys(Keys.HOME)

sorce = chrome.page_source
soup = BeautifulSoup(sorce, 'html.parser')
div = soup.find('div', {'class' : 'lazy-load loaded'})
# for all the dt and dd children in div pair always them pairwise
dts = div.find('dt', recursive=False)
dds = div.find('dd', recursive=False)
print(dts)
print(dds)
isodates = []
for date in dts:
    isodates.append(date.get('isodate'))
print(isodates)
links = []
for link in dds:
    a_tags = link.find_all('a')
    for a_tag in a_tags:
        if a_tag.get('lang') =='en':
            href = a_tag.get('href')
            links.append(href)
dateLinkDict = {}
for date, link in enumerate(isodates, links):
    dateLinkDict[date] = link
