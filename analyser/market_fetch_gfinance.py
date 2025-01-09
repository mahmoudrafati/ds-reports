import googlefinance as gf
import pandas as pd
import matplotlib.pyplot as plt

class Marketfetcher:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = {
            'USA' : '^DJI',
            'Europe' : '^STOXX50E',
            'Germany' : '^GDAXI',
            #'China' : '000001.SS',
            'China' : '^MCHI',
            #'Japan' : '^N225'
        }
        self.data = pd.DataFrame()
    
    def fetch_data(self):
        self.data = gf.download(
            list(self.tickers.values()),
            start=self.start_date,
            end=self.end_date,
            interval='1mo'
            )['Close']
        self.data.rename(columns=lambda x : list(self.tickers.keys())[list(self.tickers.values()).index(x)], inplace=True)
    
    def plot_data(self,ax):
        #ax.figure(figsize=(14, 8))
        for index in self.data.columns:
            ax.plot(self.data.index, self.data[index], label=index)
        ax.set_xlabel('Date')
        ax.set_ylabel('Closing Price')
        ax.set_title(f'Market index of {index} over time')
        ax.legend()
        #ax.tight_layout()
        #ax.show()

if __name__ == '__main__':
    fetcher = Marketfetcher('1992-01-01', '1998-01-01')
    fetcher.fetch_data()

    fig, ax = plt.subplots(figsize=(14, 8))
    fetcher.plot_data(ax)
    plt.tight_layout()
    plt.show()