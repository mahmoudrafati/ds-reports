import os
import pandas as pd


def sort_dates(df):
    return df.sort_values(by='Date')

def split_by(df, columnname):
    return df.groupby(columnname)

def save_to_csv(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, sep=';')

if __name__ == '__main__':
    base_dir = 'data/datasets/ezb'
    output_base = 'data/datasets/ezb/'

    for file in os.listdir(base_dir):
        if file.endswith('.csv'):
            csv = pd.read_csv(os.path.join(base_dir, file), sep=';')
            sorted_csv = sort_dates(csv)
            for year, year_df in split_by(sorted_csv, 'Year'):
                year_path = os.path.join(output_base, year)
                for month, month_df in split_by(year_df, 'Month'):
                    month_path = os.path.join(year_path, month)
                    save_to_csv(month_df, month_path)
                
