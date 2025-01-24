import os
import pandas as pd
import matplotlib.pyplot as plt
from gtabview import view


def safe_float_convert(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return 0.0

def sentiment_analyse(csv):
    df = pd.read_csv(csv, sep=';')
    sentiment_counts = df['sentiment'].value_counts()
    monthname = df['Month'][0]
    yearname = df['Year'][0]

    #### EVAL ####
    # count absolute
    positive_count = sentiment_counts.get('Positive', 0)
    negative_count = sentiment_counts.get('Negative', 0)
    neutral_count = sentiment_counts.get('Neutral', 0)
    total_count = positive_count + negative_count + neutral_count

    netto_sentiment = (positive_count - negative_count)/total_count
    posive_rate = positive_count/(total_count*100)

    # count relative
    if total_count > 0:
        positive_norm = positive_count / total_count * 100
        negative_norm = negative_count / total_count * 100
        neutral_norm = neutral_count / total_count * 100
    else:
        positive_norm = negative_norm = neutral_norm = 0
    total_average = (positive_norm - negative_norm)
    average_sentiment = (positive_count - negative_count) / total_count
    
    # Log message for debugging
    print(f"######## {yearname} - {monthname} ########")
    print(f"Positive: {positive_count} ({positive_norm:.2f}%)")
    print(f"Negative: {negative_count} ({negative_norm:.2f}%)")
    print(f"Neutral: {neutral_count} ({neutral_norm:.2f}%)")
    print(f"Total: {total_count}")
    print(f"Total Average: {total_average:.2f}")
    print(f"Average Sentiment: {average_sentiment:.2f}")
    print("#####################################")
    print(2*'\n')

    # Create a single row DataFrame with the monthly summary
    month_df = pd.DataFrame({
        'Year': [yearname],
        'Month': [monthname],
        'positive_count': [positive_count],
        'negative_count': [negative_count],
        'neutral_count': [neutral_count],
        'total_average': [total_average],
        'positive_norm': [positive_norm],
        'negative_norm': [negative_norm],
        'neutral_norm': [neutral_norm],
        'average_sentiment': [average_sentiment]
    })
    
    return month_df

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
            df_month = sentiment_analyse(month_file_path)
            df_year = pd.concat([df_year, df_month])
        df_years = pd.concat([df_years, df_year])
    #view(df_years)
    df_years['date'] = pd.to_datetime(df_years['Year'].astype(str) + '-' + df_years['Month'].astype(str) + '01', format='%Y-%B-%d')
    df_years = df_years.sort_values('date')

    # market data 
    word_gdp_csv = 'data/datasets/worldbank_data/worl_gdp_2k-2k23.csv'
    word_gdp = market_average(word_gdp_csv)


    #plotting 
    plot_sentiment_count(df_years)
    plot_average_sentiments(df_years)
    plot_avg_market(word_gdp, df_years)

def main():
    data_dir = 'data/datasets/'

    for bank in os.listdir(data_dir):
        if bank == '.DS_Store' or bank == 'worldbank_data':
            continue
        print(f"Analyzing data for {bank}")
        bank = os.path.join(data_dir, bank)
        analyze(bank)

if __name__ == '__main__':
    main()