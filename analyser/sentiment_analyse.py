import os
import pandas as pd
import matplotlib.pyplot as plt
from gtabview import view
import wbgapi as wb
import numpy as np
from sklearn.preprocessing import StandardScaler


def worldbank_data_fetcher():

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

    series_dict = {
        'gdp_growth': 'NY.GDP.MKTP.KD.ZG',
        'yearly_bip': "FP.CPI.TOTL.ZG",
        'real_interest_rate': 'FR.INR.RINR',
        'lending_rate': 'FR.INR.LEND',
        'unemployment_rate': 'SL.UEM.TOTL.ZS'
    }

    data_frames = {}
    for series_name, series_code in series_dict.items():
        df = wb.data.DataFrame(series_code,
                               economy=g20_countries,
                               time=range(2000, 2024),
                               labels=True)
        df = df.drop(columns=['Country'])
        df_long = df.reset_index().melt(id_vars=['economy'], var_name='Year', value_name=series_name)
        data_frames[series_name] = df
    
    merged_df = None 
    for indcator, df in data_frames.items():
        df_long = df.reset_index().melt(
            id_vars=['economy'],
            var_name='Year',
            value_name=indcator
        )
        df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})').astype(int)

        if merged_df is None:
            merged_df = df_long
        else:
            merged_df = pd.merge(merged_df, df_long, on=['economy', 'Year'], how='outer')
    return merged_df


def safe_float_convert(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return 0.0

def sentiment_analyse(csv):
    df = pd.read_csv(csv, sep=';')
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')
    
    # Falls du monthname und yearname (aus der CSV) brauchst
    date = df.loc[0, 'Date']
    monthname = df.loc[0, 'Month']
    yearname  = df.loc[0, 'Year']
    
    # Auszählen
    total_mentions = len(df)
    positive_count = (df['sentiment'] == 'Positive').sum()
    negative_count = (df['sentiment'] == 'Negative').sum()
    neutral_count  = (df['sentiment'] == 'Neutral').sum()
    
    # Kennzahlen
    if total_mentions > 0:
        net_sentiment = (positive_count - negative_count) / total_mentions
        sentiment_volatility = df['sentiment'].map({'Positive':1, 'Neutral':0, 'Negative':-1}).std()
        positive_rate = positive_count / total_mentions * 100
        negative_rate = negative_count / total_mentions * 100
        neutral_rate  = neutral_count  / total_mentions * 100
        intensity_score = (positive_count - negative_count) / total_mentions
        put_call_ratio  = positive_count / negative_count if negative_count != 0 else np.inf
        bull_bear_ratio = np.log1p(positive_count) - np.log1p(negative_count)
    else:
        # Edge-Case: keine Sätze
        net_sentiment = 0
        sentiment_volatility = 0
        positive_rate = negative_rate = neutral_rate = 0
        intensity_score = 0
        put_call_ratio = 0
        bull_bear_ratio = 0

    # Einen DataFrame mit den berechneten Werten zurückgeben
    sentiment_metrics = pd.DataFrame({
        'Date': [date],
        'Year': [yearname],
        'Month': [monthname],
        'total_mentions': [total_mentions],
        'positive_count': [positive_count],
        'negative_count': [negative_count],
        'neutral_count':  [neutral_count],
        'net_sentiment':  [net_sentiment],
        'sentiment_volatility': [sentiment_volatility],
        'positive_rate': [positive_rate],
        'negative_rate': [negative_rate],
        'neutral_rate':  [neutral_rate],
        'intensity_score': [intensity_score],
        'put_call_ratio': [put_call_ratio],
        'bull_bear_ratio': [bull_bear_ratio]
    })
    
    return sentiment_metrics

def plot_sentiment_count(data):
    df = data
    # Plot the sentiment counts
    plt.figure(figsize=(14, 8))
    plt.plot(df['date'], df['positive_count'], label='Positive', marker='', color='palegreen', linestyle='dashdot')
    plt.plot(df['date'], df['negative_count'], label='Negative', marker='', color='lightcoral', linestyle='dashdot')
    plt.plot(df['date'], df['neutral_count'], label='Neutral', marker='', color='lightgray', linestyle='dashdot')
    #calculate avg senitment by count
    #sentiment_count = df['positve'].count()
    #sentiment_sum = df['numeric_sum'].sum()
    #avg_sentiment = sentiment_sum / sentiment_count
    #df['avg_count'] = avg_sentiment
    plt.plot(df['date'], df['total_average'], label='Average Sentiment by summation')

    # Formatting the x-axis to show dates properly
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())
    plt.xticks(rotation=45)

    plt.xlabel('Date')
    plt.ylabel('Sentiment Percentage (%)')
    plt.title('Normalized Sentiments by Month with Average Sentiment')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_average_sentiments(data):
    df = data
    # Plot normalized sentiments
    plt.figure(figsize=(14, 8))
    plt.plot(df['date'], df['positive_norm'], label='Positive (%)', marker='', color='palegreen', linestyle='dotted')
    plt.plot(df['date'], df['negative_norm'], label='Negative (%)', marker='', color='lightcoral', linestyle='dotted')
    plt.plot(df['date'], df['neutral_norm'], label='Neutral (%)', marker='', color='lightgray', linestyle='dotted')
    plt.plot(df['date'], df['average_sentiment']*100, label='AverageSentiment Mean', marker='o', color='red', linestyle='--')

    # Formatting the x-axis to show dates properly
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())
    plt.xticks(rotation=45)

    plt.xlabel('Date')
    plt.ylabel('Sentiment Percentage (%)')
    plt.title('Normalized Sentiments by Month with Average Sentiment')
    plt.legend()
    #plt.tight_layout()
    plt.show()

def market_average(csv):
    df = pd.read_csv(csv, sep=',', header=0)
    print("Columns in DataFrame:", df.columns)
    print("Number of columns:", len(df.columns))
    print("Columns being looped:", df.columns[5:28])
    df_processed = pd.DataFrame()
    for col in df.columns[5:28]:
        yearname = col.split()[0]
        df[col] = df[col].apply(safe_float_convert)
        avg_year = df[col].mean()
        df_processed = pd.concat([df_processed, pd.DataFrame({'Year': [yearname], 'Average': [avg_year]})], ignore_index=True)
    df_processed['Year'] = pd.to_datetime(df_processed['Year'], format='%Y')
    df_processed = df_processed.sort_values('Year')
    # add a column showing the change in average from the previous year for each year in percent
    df_processed['Change'] = df_processed['Average'].pct_change() * 100
    view(df_processed)
    return df_processed
    # df_processed has row year 

def plot_avg_market(marketdata, sentimentdata):
    df_market = marketdata
    df_sentiment = sentimentdata
    # Plot the market data
    plt.figure(figsize=(14, 8))
    plt.plot(df_market['Year'], df_market['Change'], label='World GDP Average over all countries', marker='', color='royalblue', linestyle='solid')
    plt.plot(df_sentiment['date'], df_sentiment['average_sentiment']*100, label='Average Sentiment Noralized (%)', marker='o', color='red', linestyle='--')

    #formatting
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())
    plt.xticks(rotation=45)

    plt.xlabel('Date')
    plt.ylabel('Sentiment Percentage changes (%) and World GDP Average')
    plt.title('Normalized Sentiments by Month with Average Sentiment')
    plt.legend()
    plt.show()

def analyze(data_dir):
    df_years = pd.DataFrame()  
    for year_dir in os.listdir(data_dir):
        df_year = pd.DataFrame()
        if year_dir == '.DS_Store':
            continue
        if not os.path.isdir(os.path.join(data_dir, year_dir)):
            continue
        for month_file in os.listdir(os.path.join(data_dir, year_dir)):
            df_month = pd.DataFrame()
            if month_file == '.DS_Store':
                continue
            month_file_path = os.path.join(data_dir, year_dir, month_file)
            metrics_month = sentiment_analyse(month_file_path)
            df_year = pd.concat([df_year, metrics_month])
        df_years = pd.concat([df_years, df_year])
    #view(df_years)
    # df_years['date'] = pd.to_datetime(df_years['Year'].astype(str) + '-' + df_years['Month'].astype(str) + '01', format='%Y-%B-%d')
    df_years['Date'] = pd.to_datetime(df_years['Date'], errors='raise')
    df_years = df_years.sort_values('Date')
    #liebe dich bro, du brauchst keine wurzelbehandlung, keine sorge <3

    # market data 
    # word_gdp_csv = 'data/datasets/worldbank_data/worl_gdp_2k-2k23.csv'
    # word_gdp = market_average(word_gdp_csv)
    # markets = worldbank_data_fetcher()
    

    return df_years
    #plotting 
    # plot_sentiment_count(df_years)
    # plot_average_sentiments(df_years)
    # plot_avg_market(word_gdp, df_years)

def main():
    data_dir = 'data/datasets/'

    for bank in os.listdir(data_dir):
        if bank == '.DS_Store' or bank == 'worldbank_data':
            continue
        print(f"Analyzing data for {bank}")
        bank = os.path.join(data_dir, bank)
        bank_data = analyze(bank)
        markted_data = worldbank_data_fetcher()
        bank_agg = bank_data.groupby(['Year']).agg({
            'net_sentiment' : 'mean',
            'put_call_ratio' : 'mean',
            'sentiment_volatility' : 'mean',
            'intensity_score' : 'mean',
            'put_call_ratio' : 'mean'}
        ).reset_index()
        # df of markted data with join yeear and economy 
        market_agg = markted_data.groupby('Year', as_index=False).mean(numeric_only=True)
        merged = pd.merge(bank_agg, market_agg, on='Year', how='left')
        scaler = StandardScaler()
        merged['gdp_growth_std'] = scaler.fit_transform(merged[['gdp_growth']])
        merged['net_sentiment_std'] = scaler.fit_transform(merged[['net_sentiment']])

        print(merged.corr())
        view(merged)
        plt.plot(merged['Year'], merged['net_sentiment'], label='Net Sentiment')
        plt.plot(merged['Year'], merged['gdp_growth'], label='GDP Growth')
        plt.plot(merged['Year'], merged['put_call_ratio'], label='put coll ratio')
        plt.legend() 
        plt.title(f'Net Sentiment vs GDP Growth of {bank}')
        plt.show()
        plt.plot(merged['Year'], merged['net_sentiment_std'], label='Net Sentiment')
        plt.plot(merged['Year'], merged['gdp_growth_std'], label='GDP Growth')
        plt.legend()
        plt.title(f'Net Sentiment vs GDP Growth of {bank} (Standardized)')
        plt.show()
        
        

if __name__ == '__main__':
    main()