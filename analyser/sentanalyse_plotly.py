import os
import pandas as pd
import matplotlib.pyplot as plt
from gtabview import view
import wbgapi as wb
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# economy codes for data fetcher
G20_COUNTRIES = ["ARG", "AUS", "BRA", "CAN", "CHN", "DEU", "FRA", "GBR", "IND", "IDN", "ITA", "JPN", "KOR", "MEX", "RUS", "SAU", "ZAF", "TUR", "USA"]
US = ['USA']
EUROPE = ['DEU', 'FRA', 'GBR', 'ITA', 'EUU']
NORTH_AMERICA = ['USA', 'CAN']

# Fetch the data from the worldbank
def worldbank_data_fetcher(ecos=G20_COUNTRIES):
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
                               economy=ecos,
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
    
    market_agg = merged_df.groupby('Year', as_index=False).mean(numeric_only=True)


    return market_agg

def oecd_data_processer(csvfile, subject):
    df = pd.read_csv(csvfile)
    df_clean = df[['TIME_PERIOD','REF_AREA', 'SUBJECT' ,'OBS_VALUE']]
    df_clean['TIME_PERIOD'] = pd.to_datetime(df_clean['TIME_PERIOD'])
    df_clean = df_clean.sort_values(by='TIME_PERIOD')

    df_clean = df_clean[df_clean['SUBJECT'] == subject]
    df_clean = df_clean.rename(columns={'OBS_VALUE': subject})
    df_clean = df_clean.drop(columns=['SUBJECT'])

    return df_clean

# output: DataFrame with sentiment metrics
def sentiment_analyse(csv):
    df = pd.read_csv(csv, sep=';')
    df['Date'] = pd.to_datetime(df['Date'], errors='raise')
    
    # Falls du monthname und yearname (aus der CSV) brauchst
    date = df.loc[0, 'Date']
    # monthname = df.loc[0, 'Month']
    # yearname  = df.loc[0, 'Year']
    
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
        put_call_ratio  = positive_count / negative_count if negative_count != 0 else np.nan
        bull_bear_ratio = np.log1p(positive_count) - np.log1p(negative_count)
    else:
        # Edge-Case: keine Sätze
        net_sentiment = 0
        sentiment_volatility = 0
        positive_rate = negative_rate = neutral_rate = 0
        put_call_ratio = 0
        bull_bear_ratio = 0

    # Einen DataFrame mit den berechneten Werten zurückgeben
    sentiment_metrics = pd.DataFrame({
        'Date': [date],
        # 'Year': [yearname],
        # 'Month': [monthname],
        'total_mentions': [total_mentions],
        'positive_count': [positive_count],
        'negative_count': [negative_count],
        'neutral_count':  [neutral_count],
        'net_sentiment':  [net_sentiment],
        'sentiment_volatility': [sentiment_volatility],
        'positive_rate': [positive_rate],
        'negative_rate': [negative_rate],
        'neutral_rate':  [neutral_rate],
        'put_call_ratio': [put_call_ratio],
        'bull_bear_ratio': [bull_bear_ratio]
    })
    
    return sentiment_metrics

# Analyze the sentiment of the bank data
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

    df_years['Date'] = pd.to_datetime(df_years['Date'], errors='raise')
    df_years = df_years.sort_values('Date')
    #liebe dich bro, du brauchst keine wurzelbehandlung, keine sorge <3

    # BANK DATA TO YEAR AGGREGATION
    bank_agg = df_years.groupby(['Year']).agg({
        'net_sentiment' : 'mean',
        'put_call_ratio' : 'mean',
        'sentiment_volatility' : 'mean'}
    ).reset_index()

    bank_agg['sentiment_change'] = bank_agg['net_sentiment'].diff()

    return bank_agg

# Plotting the net sentiment of the economy based on the bank sentiment
def plot_netSentiment(data, targetmeasurement, bankname):
    df = data
    fig = make_subplots(rows=3, cols=2, subplot_titles=("GDP Growth %", "Lending Rate", "Real Interest Rate", "Lending Rate", "Unemployment Rate"))

    fig.add_trace(
        go.Scatter(x=df['Year'], y=df[targetmeasurement], mode='lines', name='Net Sentiment', line=dict(color='red')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['Year'], y=df['gdp_growth'], mode='lines', name='GDP Growth'),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=df['Year'], y=df[targetmeasurement], mode='lines', name='Net Sentiment', line=dict(color='red')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['Year'], y=df['yearly_bip'], mode='lines', name='Yearly BIP'),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(x=df['Year'], y=df[targetmeasurement], mode='lines', name='Net Sentiment', line=dict(color='red')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['Year'], y=df['real_interest_rate'], mode='lines', name='Real Interest Rate'),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(x=df['Year'], y=df[targetmeasurement], mode='lines', name='Net Sentiment', line=dict(color='red')),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=df['Year'], y=df['lending_rate'], mode='lines', name='Lending Rate'),
        row=1, col=2
    )

    fig.add_trace(
        go.Scatter(x=df['Year'], y=df[targetmeasurement], mode='lines', name='Net Sentiment', line=dict(color='red')),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=df['Year'], y=df['lending_rate'], mode='lines', name='Lending Rate'),
        row=2, col=2
    )

    fig.add_trace(
        go.Scatter(x=df['Year'], y=df[targetmeasurement], mode='lines', name='Net Sentiment', line=dict(color='red')),
        row=3, col=2
    )
    fig.add_trace(
        go.Scatter(x=df['Year'], y=df['unemployment_rate'], mode='lines', name='Unemployment Rate'),
        row=3, col=2
    )

    fig.update_layout(
        title=f'{targetmeasurement} of G20 Countries (Standardized) based on {bankname} Sentiment',
        height=800
    )
    fig.show()

def plot_information(data, bankname):
    # Plot feature correlations
    import plotly.express as px
    correlation = data[['net_sentiment_std', 'put_call_ratio_std', 'sentiment_volatility', 'gdp_growth_std', 'yearly_bip_std', 'real_interest_rate_std', 'lending_rate_std', 'unemployment_rate_std']].corr()
    df = pd.DataFrame(correlation)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(df)

    fig = px.imshow(correlation, text_auto=True, title=f'Feature Correlation Matrix based on {bankname.split("/")[-1]}')
    fig.show()
    
    # Feature importance using Random Forest
    from sklearn.ensemble import RandomForestRegressor
    X = data[['net_sentiment_std', 'put_call_ratio_std', 'sentiment_volatility' ,'yearly_bip_std', 'real_interest_rate_std', 'lending_rate_std', 'unemployment_rate_std']]
    y = data['gdp_growth_std'].fillna(0)  
    model = RandomForestRegressor()
    model.fit(X, y)
    importance = pd.Series(model.feature_importances_, index=X.columns)
    fig = px.bar(importance, x=importance.values, y=importance.index, orientation='h', title=f'Feature Importances on Net Sentiment based on {bankname.split("/")[-1]}')
    fig.show()

def main():
    data_dir = 'data/datasets/'

    for bank in os.listdir(data_dir):
        if bank == '.DS_Store' or bank == 'worldbank_data':
            continue
        print(f"Analyzing data for {bank}")
        bank = os.path.join(data_dir, bank)
        bank_agg = analyze(bank)
        market_agg_g20 = worldbank_data_fetcher()
        # market_agg_us = worldbank_data_fetcher(US)
        # market_agg_europe = worldbank_data_fetcher(EUROPE)
        # market_agg_na = worldbank_data_fetcher(NORTH_AMERICA)
        
        # df of markted data with join yeear and economy 
        merged_g20 = pd.merge(bank_agg, market_agg_g20, on='Year', how='left')
        # merged_us = pd.merge(bank_agg, market_agg_us, on='Year', how='left')
        # merged_europe = pd.merge(bank_agg, market_agg_europe, on='Year', how='left')
        # merged_na = pd.merge(bank_agg, market_agg_na, on='Year', how='left')

        # Standardize the data
        scaler = StandardScaler()
        columns_to_scale = ['gdp_growth', 'yearly_bip', 'real_interest_rate', 'lending_rate', 'unemployment_rate', 'put_call_ratio', 'net_sentiment', 'sentiment_change']
        for col in columns_to_scale:
            merged_g20[f'{col}_std'] = scaler.fit_transform(merged_g20[[col]])
            # merged_us[f'{col}_std'] = scaler.fit_transform(merged_us[[col]])
            # merged_europe[f'{col}_std'] = scaler.fit_transform(merged_europe[[col]])
            # merged_na[f'{col}_std'] = scaler.fit_transform(merged_na[[col]])

        merged = merged_g20 
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=merged['Year'], y=merged['net_sentiment_std'], mode='lines', name='Net Sentiment std', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=merged['Year'], y=merged['sentiment_change_std'], mode='lines', name='Net Sentiment change std', line=dict(color='lightcoral')))
        fig.add_trace(go.Scatter(x=merged['Year'], y=merged['gdp_growth_std'], mode='lines', name='GDP Growth std', line=dict(color='cornflowerblue')))
        
        fig.update_layout(
            title=f'Standardized Metrics based on {bank.split("/")[-1]} Sentiment',
            xaxis_title='Year',
            yaxis_title='Standardized Values',
            legend_title='Metrics',
            height=600
        )
        fig.show()
        plot_netSentiment(merged, 'gdp_growth_std', bank)

        # Plot additional information
        plot_information(merged, bank.split("/")[-1])
        # plot_netSentiment(merged_g20, 'net_sentiment_std', bank)
        # plot_netSentiment(merged_g20, 'put_call_ratio_std', bank)
        
if __name__ == '__main__':
    main()