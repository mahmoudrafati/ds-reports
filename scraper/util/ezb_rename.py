import os
import pandas as pd

base_dir = 'data/raw_pdf/ezb'


for year in os.listdir(base_dir):
    if os.path.isdir(os.path.join(base_dir, year)):
        for file in os.listdir(os.path.join(base_dir, year)):
            if file.endswith('.csv'):
                df = pd.read_csv(os.path.join(base_dir, year, file), sep=';')
                monthname = pd.to_datetime(df['Date'], errors='raise').dt.strftime('%B').iloc[0] + '.csv'
                os.rename(os.path.join(base_dir, year, file), os.path.join(base_dir, year, monthname))
            else:
                continue
    else:
        continue