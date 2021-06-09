import os
from kucoin.client import Market
from math import floor

def extract_volume(json):
    try:
        return float(json['volValue']) # return volume in USDT traded in past 24h
    except KeyError:
        return 0

#Clear out tickers and signal files
if os.path.exists('./tickers.txt'):
     os.remove('./tickers.txt')
if os.path.exists('./signalsample.txt'):
     os.remove('./signalsample.txt')

market = Market(url='https://api.kucoin.com')
tickers = market.get_all_tickers()['ticker']
tickers = [x for x in tickers if "USDT" in x['symbolName']] # only get symbols containing USDT
tickers.sort(key=extract_volume, reverse=True) # sort list by volume traded in USDT in past 24h
tickers = tickers[:floor(len(tickers)*.25)] # trim list to top 25% based on traded volume
stable_coins = ['USDT','USDC','BUSD','DAI','BTCB','UST','TUSD','PAX','HUSD','RSR','USDN','GUSD','FEI','LUSD','FRAX','VAI','EURS','QC', 'USDJ','SUSD']

# save to files
for ticker in tickers:
    if not ticker['symbolName'].split("-")[0] in stable_coins:
        with open('./tickers.txt','a+') as f:
            f.write(ticker['symbolName'].split("-")[0] + '\n')

for ticker in tickers:
    if not ticker['symbolName'].split("-")[0] in stable_coins:
        with open('./signalsample.txt','a+') as f:
            f.write(ticker['symbolName'].split("-")[0] + '\n')