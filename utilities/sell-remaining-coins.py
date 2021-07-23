import sys, json, os, argparse, yaml, time
from kucoin.client import Trade, Market
from datetime import datetime

from colorama import init
init()

# for colourful logging to the console
class txcolors:
    BUY = '\033[92m'
    WARNING = '\033[93m'
    SELL_LOSS = '\033[91m'
    SELL_PROFIT = '\033[32m'
    DIM = '\033[2m\033[35m'
    DEFAULT = '\033[39m'

def load_config(file):
    try:
        with open(file) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError as fe:
        exit(f'Could not find {file}')
    
    except Exception as e:
        exit(f'Encountered exception...\n {e}')

def parse_args():
    x = argparse.ArgumentParser()
    x.add_argument('--debug', '-d', help="extra logging", action='store_true')
    x.add_argument('--config', '-c', help="Path to config.yml")
    x.add_argument('--creds', '-u', help="Path to creds file")
    x.add_argument('--notimeout', help="Dont use timeout in prod", action="store_true")
    return x.parse_args()

def load_correct_creds(creds):
    return creds['prod']['key'], creds['prod']['secret'], creds['prod']['passphrase']

def get_order_price(orderId):
    fills = trader.get_fill_list(orderId=orderId, tradeType='TRADE')['items']
    while fills == []: # keep going until kucoin fills
        fills = trader.get_fill_list(orderId=orderId, tradeType='TRADE')['items']
        time.sleep(0.5)
    # get correct decimal places
    coin_info = list(filter(lambda x:x["symbol"]==fills[0]['symbol'],full_symbol_list)) # search the master list for correct coin
    decimal_length = coin_info[0]['baseIncrement'].index('1') - 1
    # weighted_avg = (price * size for each fill) / total order size
    weighted_avg = round(sum(float(fill['price']) * float(fill['size']) for fill in fills)
        / sum(float(fill['size']) for fill in fills), decimal_length)
    return str(weighted_avg)

def get_coin_price(symbol):
    price = market.get_ticker(symbol)['price']
    return str(price)

args = parse_args()

DEFAULT_CONFIG_FILE = './config.yml'
DEFAULT_CREDS_FILE = './creds.yml'
ORDERS_FILE = 'coin_orders.json'
PROFIT_HISTORY_FILE = 'profit_history.json'

config_file = args.config if args.config else DEFAULT_CONFIG_FILE
creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
parsed_creds = load_config(creds_file)
parsed_config = load_config(config_file)

TEST_MODE = parsed_config['script_options'].get('TEST_MODE')
LOG_TRADES = parsed_config['script_options'].get('LOG_TRADES')
LOG_FILE = parsed_config['script_options'].get('LOG_FILE')

if TEST_MODE:
    ORDERS_FILE = 'test_' + ORDERS_FILE
    PROFIT_HISTORY_FILE = 'test_' + PROFIT_HISTORY_FILE
    LOG_FILE = 'test_' + LOG_FILE

ORDERS_FILE_PATH = './' + ORDERS_FILE
PROFIT_HISTORY_FILE_PATH = './' + PROFIT_HISTORY_FILE
LOG_FILE_PATH = './' + LOG_FILE

key, secret, passphrase = load_correct_creds(parsed_creds)

trader = Trade(key, secret, passphrase, is_sandbox=False, url='')
market = Market(url='https://api.kucoin.com')
full_symbol_list = market.get_symbol_list() # get master list of symbols

def write_log(logline):
    timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
    with open(LOG_FILE_PATH,'a+') as f:
        f.write(timestamp + ' ' + logline + '\n')

with open(ORDERS_FILE_PATH, 'r') as f:
    orders = json.load(f)
    total_profit = 0
    total_price_change = 0

    for order in list(orders):

        coin = orders[order]['symbol']

        if not TEST_MODE:
            sell_coin = trader.create_market_order(
                symbol = coin,
                side = 'SELL',
                size = orders[order]['volume']
            )
            LastPrice = float(get_order_price(sell_coin['orderId']))
        else:
            LastPrice = float(get_coin_price(coin))

        BuyPrice = float(orders[order]['bought_at'])
        profit = (LastPrice - BuyPrice) * orders[order]['volume']
        PriceChange = float((LastPrice - BuyPrice) / BuyPrice * 100)

        total_profit += profit
        total_price_change += PriceChange

        text_color = txcolors.SELL_PROFIT if PriceChange >= 0. else txcolors.SELL_LOSS
        console_log_text = f"{text_color}Sell: {orders[order]['volume']} {coin} - {BuyPrice} - {LastPrice} Profit: {profit:.2f} {PriceChange:.2f}%{txcolors.DEFAULT}"
        print(console_log_text)


        if LOG_TRADES:
            timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
            write_log(f"Sell: {orders[order]['volume']} {coin} - {BuyPrice} - {LastPrice} Profit: {profit:.2f} {PriceChange:.2f}%")

    text_color = txcolors.SELL_PROFIT if total_price_change >= 0. else txcolors.SELL_LOSS
    print(f"Total Profit: {text_color}{total_profit:.2f}{txcolors.DEFAULT}. Total Price Change: {text_color}{total_price_change:.2f}%{txcolors.DEFAULT}")

with open(PROFIT_HISTORY_FILE_PATH, 'r') as f:
    profit_history = json.load(f)
    
profit_history = profit_history + total_price_change

with open(PROFIT_HISTORY_FILE_PATH, 'w') as file:
    json.dump(profit_history, file, indent=4)

os.remove(ORDERS_FILE_PATH)