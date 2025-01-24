import wbgapi as wb
import pandas as pd
from gtabview import view
# G20-Ländercodes (teils Kürzel für EU/EUR kann variieren)
g20_countries = [
    "ARG",  # Argentinien
    "AUS",  # Australien
    "BRA",  # Brasilien
    "CAN",  # Kanada
    "CHN",  # China
    "DEU",  # Deutschland
    "FRA",  # Frankreich
    "GBR",  # Großbritannien
    "IND",  # Indien
    "IDN",  # Indonesien
    "ITA",  # Italien
    "JPN",  # Japan
    "KOR",  # Südkorea
    "MEX",  # Mexiko
    "RUS",  # Russland
    "SAU",  # Saudi-Arabien
    "ZAF",  # Südafrika
    "TUR",  # Türkei
    "USA",  # USA
    # "EUU"  # Europäische Union (optional)
]

# Beispiel: Arbeitslosenquote (Indicator Code: SL.UEM.TOTL.ZS)
gdp_growth = 'NY.GDP.MKTP.KD.ZG'
yearly_bip = "FP.CPI.TOTL.ZG"
real_interest_rate = 'FR.INR.RINR'
lending_rate = 'FR.INR.LEND'
unemployment_rate = 'SL.UEM.TOTL.ZS'

# Lade Daten von 2000 bis 2023 (falls verfügbar)
# Output im 'wide' Format (pro Land eine Spalte)
df = wb.data.DataFrame([gdp_growth, yearly_bip, real_interest_rate, lending_rate, unemployment_rate],
                       economy=g20_countries,
                       time=range(2000, 2024),
                       labels=True)

df_slim = df.drop(columns=['Country'])

df_long = df_slim.reset_index().melt(
    id_vars=['economy', 'Series', 'series'],
    ignore_index=True
)

grou_long = df_long.groupby(['series'])

# Optional: in ein 'long format' transformieren (besser für Zeitreihen)
# df_long = df.reset_index().melt(
#     id_vars=['economy', 'Country'],
#     ignore_index=True
# )
# # df_long.rename(columns={'economy':'country', 'time':'year'}, inplace=True)

# view(df_long.tail(6))

# view(df.head(15))
print(df_long.head(5))
print(grou_long.head(5))