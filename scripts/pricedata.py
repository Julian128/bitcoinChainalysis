import pycoingecko
import matplotlib.pyplot as plt
import json

coinGecko = pycoingecko.CoinGeckoAPI()
btc_data = coinGecko.get_coin_market_chart_by_id('bitcoin', 'usd', '5000days')
dates = [data[0] for data in btc_data['prices']]
price = [data[1] for data in btc_data['prices']]

# dict of timestamps and prices
data = {dates[i]: price[i] for i in range(len(dates))}
with open('btc_data.json', 'w') as f:
    json.dump(data, f)