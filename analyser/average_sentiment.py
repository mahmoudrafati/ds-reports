import os
import pandas as pd
import matplotlib.pyplot as plt
from gtabview import view

data_dir_string =  'data/datasets'
data_dir_path = os.path.abspath(data_dir_string)

def sentiment_count(csv_path): 
    df = pd.read_csv(csv_path, sep=';')
    sentiment_counts =  df['sentiment'].value_counts()
    # extract year and month from path
    monthname = os.path.basename(os.path.normpath(csv_path))
    yearname = os.path.basename(os.path.dirname(csv_path))
    # add column year and month as datetme in df for each sentence
    try:
        df['year'] = pd.to_datetime(yearname, format='%Y')
    except ValueError:
        print(f'ERROR: Could not convert {yearname} to datetime')
        df['year'] = pd.NaT
    try:
        month = monthname.split('.')[0]
        df['month'] = pd.to_datetime(month, format='%b')
    except ValueError:
        print(f'ERROR: Could not convert {month} to datetime')
        df['month'] = pd.NaT

    print(f'######## EVALUATION FOR YEAR {yearname} {monthname} ########')

    positive_count = sentiment_counts.get('positive', 0)
    negative_count = sentiment_counts.get('negative', 0)
    neutral_count = sentiment_counts.get('neutral', 0)

    print(f'Positive Sentiments: {positive_count}')
    print(f'Negative Sentiments: {negative_count}')
    print(f'Neutral Sentiments: {neutral_count}')

    # Normalize the counts
    total_count = positive_count + negative_count + neutral_count
    if total_count > 0:
        positive_norm = positive_count / total_count * 100 
        negative_norm = negative_count / total_count * 100
        neutral_norm = neutral_count / total_count * 100
    else:
        positive_norm = negative_norm = neutral_norm = 0
    total_average = (positive_norm - negative_norm)
    average_sentiment = (positive_count - negative_count)/total_count

    return df, {
        'year': pd.to_datetime(yearname, format='%Y').year,
        'month': pd.to_datetime(month, format='%b').month,
        'positive': positive_count,
        'negative': negative_count,
        'neutral': neutral_count,
        'total': total_count,
        'total_average': total_average,
        'average_sentiment': average_sentiment,
        'positive_norm': positive_norm,
        'negative_norm': negative_norm,
        'neutral_norm': neutral_norm
    }

def plot_data_courier(data):
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    # Combine year and month into a single datetime column for accurate plotting
    df['date'] = pd.to_datetime(df['year'].astype(str)+'-'+df['month'].astype(str), format='%Y-%m')
    # Sort the DataFrame by date
    df = df.sort_values('date')
    return df

def plot_sentiment_count(data):
    df = data
    # Plot the sentiment counts
    plt.figure(figsize=(14, 8))
    plt.plot(df['date'], df['positive'], label='Positive', marker='', color='palegreen', linestyle='dashdot')
    plt.plot(df['date'], df['negative'], label='Negative', marker='', color='lightcoral', linestyle='dashdot')
    plt.plot(df['date'], df['neutral'], label='Neutral', marker='', color='lightgray', linestyle='dashdot')
    #calculate avg senitment by count
    #sentiment_count = df['positve'].count()
    #sentiment_sum = df['numeric_sum'].sum()
    #avg_sentiment = sentiment_sum / sentiment_count
    #df['avg_count'] = avg_sentiment
    plt.plot(df['date'], df['total_average'], label='Average Sentiment by summation')

    # Formatting the x-axis to show dates properly
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=1))
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
    # Calculate average sentiment_numeric per month
    #avg_sentiment = df[['positive_norm', 'negative_norm', 'neutral_norm']].mean(axis=1)
    # Overlay the average sentiment
    #plt.plot(df['date'], avg_sentiment, label='Average Sentiment (%)', color='red', linestyle='--', marker='x')

    # Formatting the x-axis to show dates properly
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=1))
    plt.xticks(rotation=45)

    plt.xlabel('Date')
    plt.ylabel('Sentiment Percentage (%)')
    plt.title('Normalized Sentiments by Month with Average Sentiment')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    sentiment_data = []
    data_dir = data_dir_path

    for bank_dir in os.listdir(data_dir):
            if bank_dir == '.DS_Store':
                continue
            bank_path = os.path.join(data_dir, bank_dir)

            if not os.path.isdir(bank_path):
                continue

            for year_dir in os.listdir(bank_path):
                sentiment_data_year = []
                if year_dir == '.DS_Store':
                    continue
                year_path = os.path.join(bank_path, year_dir)

                if not os.path.isdir(year_path):
                    continue
                    
                for subyear_dir in os.listdir(year_path):
                    if subyear_dir == '.DS_Store' or subyear_dir == 'links.json':
                        continue
                    subyear_path = os.path.join(year_path, subyear_dir)
                    if not os.path.exists(subyear_path):
                        continue
                    # edit files in subyear dir 
                    for csv_file in os.listdir(subyear_path):
                        csv_path = os.path.join(subyear_path, csv_file)
                        df, sentiment_values = sentiment_count(csv_path)
                        #df['sentiment_numeric'] = df['sentiment'].map({'positive': 1, 'neutral': 0, 'negative': -1})
                        #df['numeric_mean'] = df['sentiment_numeric'].mean()
                        #df['numeric_sum'] = df['sentiment_numeric'].sum()
                        #sentiment_values['avg_mean'] = average_sentiment
                        #sentiment_values['avg_sum'] = average_sentiment
                        sentiment_data_year.append(sentiment_values)
                        #print(f'Average Sentiment: {average_sentiment}')
                if sentiment_data_year:
                    # flatten list for plotting 
                    plot_data = plot_data_courier(sentiment_data_year)
                    view(plot_data)
                    flat_data = [item for sublist in sentiment_data_year for item in sublist]
                    #plot_average_sentiments(flat_data)
                    plot_sentiment_count(plot_data)
                    plot_average_sentiments(plot_data)
                #plot_average_sentiments(sentiment_data)