# import pandas , bs4 and requests 
from bs4 import BeautifulSoup
import requests as req
import pandas as pd

# Url of the main EZB Monetary Policy page
url = 'https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html'

# Get the page content
response = req.get(url)

# Parse the page content
soup = BeautifulSoup(response.content, 'html.parser')
print(soup.prettify())
