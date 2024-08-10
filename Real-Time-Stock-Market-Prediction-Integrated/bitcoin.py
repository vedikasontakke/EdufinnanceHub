import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request

app = Flask(__name__)

# Function to fetch cryptocurrency data
def fetch_crypto_data(crypto_id):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=1'
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching data")
        return None

    return response.json()

def plot_candlestick(data):
    data['date'] = mdates.date2num(data.index)
    new_data = data[['date', 'open', 'high', 'low', 'close']].values

    fig, ax = plt.subplots()
    candlestick_ohlc(ax, new_data, width=0.0005, colorup='#53c156', colordown='#ff1717')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.title('Candlestick chart')
    plt.xticks(rotation=45)

    # Save the plot to a temporary file
    plot_file = '/tmp/crypto_plot.png'
    plt.savefig(plot_file)
    plt.close()

    return plot_file

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        crypto_id = request.form.get("crypto_id")

        data = fetch_crypto_data(crypto_id)

        if data is not None:
            # Convert data to DataFrame
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Create OHLC data
            ohlc_data = df['price'].resample('1H').ohlc()

            # Plot candlestick and get the plot file path
            plot_file = plot_candlestick(ohlc_data)

            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Cryptocurrency Candlestick Chart</title>
            </head>
            <body>
                <h1>Cryptocurrency Candlestick Chart for {crypto_id}</h1>
                <img src="{plot_file}" alt="Candlestick Chart">
            </body>
            </html>
            """
        else:
            return "Error fetching data. Please try again."

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Enter Cryptocurrency ID</title>
    </head>
    <body>
        <h1>Enter Cryptocurrency ID</h1>
        <form method="POST" action="/">
            <label for="crypto_id">Enter Cryptocurrency ID (e.g., bitcoin):</label>
            <input type="text" id="crypto_id" name="crypto_id" required><br><br>
            <button type="submit">Generate Chart</button>
        </form>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, port=5003)
