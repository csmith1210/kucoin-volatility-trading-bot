# get the top 30 coinmarketcap gainers for the past 7d
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from kucoin.client import Market
import os, json, yaml, time

if os.path.exists('./signalsample.txt'):
     os.remove('./signalsample.txt')

def load_config(file):
    try:
        with open(file) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError as fe:
        exit(f'Could not find {file}')
    except Exception as e:
        exit(f'Encountered exception...\n {e}')

CREDS_FILEPATH = './creds.yml' # replace with path to your creds file
parsed_creds = load_config(CREDS_FILEPATH)
coinmarketcap_API_key = parsed_creds['cmc']['key']
stable_coins = ['USDT','USDC','BUSD','DAI','BTCB','UST','TUSD','PAX','HUSD','RSR','USDN','GUSD','FEI','LUSD','FRAX','VAI','EURS','QC', 'USDJ','SUSD']

# set up API call
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'1000', # number of tickers to return
  'sort':'percent_change_7d', # sort based on % change in 7d and sort desc automatically
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': coinmarketcap_API_key,
}
session = Session()
session.headers.update(headers)
# call API
try:
  response = session.get(url, params=parameters)
  tickers = json.loads(response.text)['data']
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)

market = Market(url='https://api.kucoin.com')
tracker = 0
for ticker in tickers:
  if tracker >= 30:
    break
  symbol = ticker['symbol'] + '-USDT'
  kucoin_ticker = market.get_24h_stats(symbol)
  if not kucoin_ticker['volValue'] == None and float(kucoin_ticker['volValue']) >= 500000:
    tracker += 1
    if ticker['symbol'] not in stable_coins:
      with open('./signalsample.txt','a+') as f1:
        f1.write(ticker['symbol'] + '\n')
      with open('./tickers.txt','a+') as f2:
        f2.seek(0, os.SEEK_SET)
        line_found = any(ticker['symbol'] in line for line in f2)
        if not line_found:
          f2.seek(0, os.SEEK_END)
          f2.write(ticker['symbol'] + '\n')