import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import datetime as dt
import pandas as pd
import bs4 as bs
import pickle
import requests
import os
import yfinance as yf

style.use('ggplot')


# Extract Current top 50 Stocks which are part of Nifty50
def save_nifty50_tickers():
    resp = requests.get('https://en.wikipedia.org/wiki/NIFTY_50')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text
        tickers.append(ticker.strip())
    with open('NIFTY_50.pickle', 'wb') as f:
        pickle.dump(tickers, f)

    return tickers


# Get 1 min data for each symbol within a period of 7 days
def get_data_from_yahoo(reload_nifty50=False):
    if reload_nifty50:
        tickers = save_nifty50_tickers()
    else:
        with open('NIFTY_50.pickle', 'rb') as f:
            tickers = pickle.load(f)

    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    for ticker in tickers:
        try:
            df = yf.download(ticker, period='7d', interval='1m')
            if df.empty:
                print(f"No data returned for {ticker}.")
            else:
                df.to_csv(f'stock_dfs/{ticker}.csv')
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")


# Join the Adj Close columns of all the csv file into a single dataframe replace the name with ticker
def compile_data():
    get_data_from_yahoo(True)
    with open('NIFTY_50.pickle', 'rb') as f:
        tickers = pickle.load(f)
    main_df = pd.DataFrame()

    for ticker in tickers:
        df = pd.read_csv(f'stock_dfs/{ticker}.csv')
        df.set_index('Datetime', inplace=True)

        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

    main_df.to_csv('nifty50_joined.csv')


# Visualizing the correlation on returns of the stocks to see if they follow normal distribution
def visualize_data():
    compile_data()
    df = pd.read_csv('nifty50_joined.csv')
    df.set_index('Datetime', inplace=True)

    df_corr = df.pct_change().corr()

    data = df_corr.values
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(1, 1, 1)
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlBu)
    fig.colorbar(heatmap)

    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)

    ax.invert_yaxis()
    ax.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index

    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)

    plt.xticks(rotation=90)
    heatmap.set_clim(-1, 1)
    plt.tight_layout()
    fig.savefig('heatmap.png')


# Run the visualization
if __name__ == "__main__":
    visualize_data()
