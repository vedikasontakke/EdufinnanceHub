import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
from flask import Flask, render_template, request

app = Flask(__name__)

# Replace with your own Alpha Vantage API key
api_key = '669835009387f9.87422928'
ts = TimeSeries(key=api_key, output_format='pandas')


# Function to fetch intraday data
def fetch_data(stock, interval):
    try:
        data, _ = ts.get_intraday(symbol=stock, interval=interval, outputsize='full')
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        stock = request.form.get("stock")
        interval = request.form.get("interval")

        # Call function to fetch data
        data = fetch_data(stock, interval)

        if data is not None:
            data['date'] = data.index.map(mdates.date2num)
            new_data = data[['date', '1. open', '2. high', '3. low', '4. close', '5. volume']].values

            fig, ax = plt.subplots()

            # Create candlestick chart
            candlestick_ohlc(ax, new_data, width=0.0005, colorup='#53c156', colordown='#ff1717')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            plt.title(f'Candlestick chart for {stock} at {interval}')
            plt.xticks(rotation=45)

            # Save the plot to a temporary file
            plot_file = '/tmp/plot.png'
            plt.savefig(plot_file)
            plt.close()

            return render_template('stocks.html', stock=stock, interval=interval, plot_file=plot_file)
        else:
            return "Error fetching data. Please try again."

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Stock Candlestick Chart</title>
    </head>
    <body>
        <h1>Stock Candlestick Chart</h1>
        <form method="POST" action="/">
            <label for="stock">Enter Stock Symbol:</label>
            <input type="text" id="stock" name="stock" required><br><br>
            <label for="interval">Enter Interval (1, 5, 15, 30):</label>
            <input type="text" id="interval" name="interval" required><br><br>
            <button type="submit">Generate Chart</button>
        </form>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5002)
