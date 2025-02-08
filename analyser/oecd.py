from gtabview import view 
import urllib.request
import pandas as pd
import plotly.express as px
import os 
from tqdm import tqdm

format = '&format=csvfilewithlabels'

urls = {
   'cpi': 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_G20_PRICES@DF_G20_PRICES,1.0/G20.M...PC...?startPeriod=1999-01' + format,
   'gdp': 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA_EXPENDITURE_GROWTH_G20,1.1/Q..G7.S1..B1GQ......G1.?startPeriod=1999-Q1' + format,
   'uep': 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_LFS@DF_IALFS_INDIC,/G7.UNE_LF_M...Y._T.Y_GE15..M?startPeriod=1999-01' + format,
   'longterm_ir': 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/CAN+DEU+ITA+FRA+JPN+GBR+USA.M.IRLT......?startPeriod=1999-01' + format,
   'shortterm_ir': 'https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/CAN+DEU+ITA+FRA+JPN+GBR+USA.M.IR3TIB......?startPeriod=1999-01' + format
}

headers = {'User-Agent': 'Mozilla/5.0'}
output_dir = 'data/raw_pdf/oecd/'
os.makedirs(os.path.dirname(output_dir), exist_ok=True)

for key, value in tqdm(urls.items(), desc='Downloading..') :
   req = urllib.request.Request(value, headers=headers)
   # create ds 
   with urllib.request.urlopen(req) as resp:
      df = pd.read_csv(resp)
   df.to_csv(output_dir+key+'_raw.csv', sep=';', index=False)

   df_plot = df[['TIME_PERIOD','REF_AREA' ,'OBS_VALUE']]
   df_plot['TIME_PERIOD'] = pd.to_datetime(df_plot['TIME_PERIOD'])
   df_plot = df_plot.sort_values(by='TIME_PERIOD')

   # plot
   fig = px.line(df_plot, x='TIME_PERIOD', y='OBS_VALUE', title=f'{key} rate', labels={'TIME_PERIOD': 'Date', 'OBS_VALUE' : 'rate'}, color='REF_AREA')
   fig.show()

# view(df_gdp)
# df_new_umempl = df_unempl[['TIME_PERIOD', 'OBS_VALUE']]
# df_new_umempl['TIME_PERIOD'] = pd.to_datetime(df_new_umempl['TIME_PERIOD'])
# df_new_umempl = df_new_umempl.sort_values(by='TIME_PERIOD')
# view(df_new_umempl)

# df_gdp = df_gdp[['TIME_PERIOD', 'OBS_VALUE']]
# df_gdp['TIME_PERIOD'] = pd.to_datetime(df_gdp['TIME_PERIOD'])
# df_gdp = df_gdp.sort_values(by='TIME_PERIOD')
# view(df_gdp)

# # plot with plotly where x is df['TIME_PERIOD'] and y is df['OBS_VALUE']
# fig = px.line(df_new_umempl, x='TIME_PERIOD', y='OBS_VALUE', title='OECD Unemployment Rate G7', labels={'TIME_PERIOD': 'Year', 'OBS_VALUE': 'Unemployment Rate'})
# fig.show()

# fig = px.line(df_gdp, x='TIME_PERIOD', y='OBS_VALUE', title='OECD GDP Growth Rate G7', labels={'TIME_PERIOD': 'Year', 'OBS_VALUE': 'GDP Growth Rate'})
# fig.show()

