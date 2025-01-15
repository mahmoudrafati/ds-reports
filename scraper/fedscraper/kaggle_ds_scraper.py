import os
import re
import nltk
import pandas as pd
import sys
from nltk.tokenize import word_tokenize, sent_tokenize
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from tqdm import tqdm
from gtabview import view

def process_file(year, output_path):
    df_year = pd.read_csv(year, sep=';')
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    #turn date column to datetime 
    df_year['Date'] = pd.to_datetime(df_year['Date'], errors='raise')
    df_year['Month'] = df_year['Date'].dt.strftime('%B')
    for name, group in df_year.groupby(df_year['Month']):
        group.to_csv(f'{os.path.join(output_path, name)}.csv', sep=';', index=False)
    #create new csv grouped by month (YYYY-MM-DD)
    #grouped = df_year.groupby('Month')
    #view(grouped)


def main():
    raw_path_string = 'data/raw_pdf/kaggledata_year/'
    output_path_string = 'data/raw_pdf/kaggledata_month'
    raw_path = os.path.abspath(raw_path_string)

    for year_file in os.listdir(raw_path):
        year_file_name = year_file.split('.')[0]
        if year_file == '.DS_Store' or year_file == 'cleaned_pro_FOMC.csv': 
            continue
        year_path = os.path.join(raw_path, year_file)

        if not os.path.exists(year_path):
            continue
        output_year_path = os.path.join(output_path_string, year_file_name)
        process_file(year_path, output_year_path)
        print('Done')

if __name__ == '__main__':
    main()
