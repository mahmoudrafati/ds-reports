# OLD PLOTS NOT USED ANYMORE

# BASIC SENTIMENT COUNTS
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

# NORMALIZED SENTIMENT COUNTS
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


# market plot_average_sentiments
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