import ccxt
import time
import logging
import os  # For environment variables
import argparse  # For command-line arguments

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the exchange with environment variables for API keys

api_key = os.getenv("di")
api_secret = os.getenv("secret")
exchange = ccxt.phemex({
    'apiKey': api_key,
    'secret': api_secret,
    'timeout': 30000,
    'enableRateLimit': True,
})
# Command-line argument parsing for configurability
parser = argparse.ArgumentParser(description='Grid Trading Bot')
parser.add_argument('--grid_size', type=int, default=100, help='Number of grid levels')
parser.add_argument('--price_min', type=float, default=1.9118, help='Minimum price for the grid')
parser.add_argument('--price_max', type=float, default=3.4322, help='Maximum price for the grid')
parser.add_argument('--order_amount', type=float, default=1.1/exchange.fetch_ticker("WIF/USDT")['last'], help='Amount to trade at each level')
parser.add_argument('--time_interval', type=int, default=10, help='Time between grid checks (seconds)')
args = parser.parse_args()

# Grid parameters from command-line arguments
base_asset = "WIF"
quote_asset = "USDT"
pair = f"{base_asset}/{quote_asset}"
grid_size = args.grid_size
price_min = args.price_min
price_max = args.price_max
order_amount = args.order_amount
time_interval = args.time_interval

# Function to calculate grid levels
def calculate_grid_levels(price_min, price_max, grid_size):
    price_step = (price_max - price_min) / (grid_size - 1)
    return [price_min + i * price_step for i in range(grid_size)]

# Function to fetch current price
def fetch_current_price():
    ticker = exchange.fetch_ticker(pair)
    return (ticker['bid'] + ticker['ask']) / 2

# Function to fetch open orders
def fetch_open_orders():
    try:
        return exchange.fetch_open_orders(pair)
    except Exception as e:
        logging.error(f"Error fetching open orders: {e}")
        return []

# Function to cancel all open orders outside of grid levels
def cancel_unnecessary_orders(open_orders, grid_levels, price_step):
    for order in open_orders:
        if order['side'] == 'buy':
            if order['price'] not in grid_levels:
                try:
                    exchange.cancel_order(order['id'], pair)
                    logging.info(f"Canceled unnecessary buy order at {order['price']}")
                except Exception as e:
                    logging.error(f"Error canceling buy order at {order['price']}: {e}")
        elif order['side'] == 'sell':
            sell_price = grid_levels[open_orders.index(order)] + price_step
            if order['price'] != sell_price:
                try:
                    exchange.cancel_order(order['id'], pair)
                    logging.info(f"Canceled unnecessary sell order at {order['price']}")
                except Exception as e:
                    logging.error(f"Error canceling sell order at {order['price']}: {e}")

# Function to create or maintain the grid
def manage_grid(grid_levels, order_amount, open_orders):
    for level in grid_levels:
        # Ensure there's a buy order at this grid level
        buy_orders = [o for o in open_orders if o['side'] == 'buy' and o['price'] == level]
        if not buy_orders:
            try:
                buy_order = exchange.create_limit_buy_order(pair, order_amount, level)
                logging.info(f"Created new buy order at {level}: {buy_order}")
            except Exception as e:
                logging.error(f"Error creating buy order at {level}: {e}")

        # Ensure there's a sell order at the corresponding sell level
        sell_price = level + (grid_levels[1] - grid_levels[0])
        sell_orders = [o for o in open_orders if o['side'] == 'sell' and o['price'] == sell_price]
        if not sell_orders:
            try:
                sell_order = exchange.create_limit_sell_order(pair,(order_amount-(0.0001*order_amount)), sell_price)
                logging.info(f"Created new sell order at {sell_price}: {sell_order}")
            except Exception as e:
                logging.error(f"Error creating sell order at {sell_price}: {e}")

# Main loop for continuous operation
def grid_trading_bot():
    grid_levels = calculate_grid_levels(price_min, price_max, grid_size)
    
    while True:
        try:
            open_orders = fetch_open_orders()
            current_price = fetch_current_price()
            logging.info(f"Current price: {current_price}")

            # Cancel unnecessary orders outside the grid
            cancel_unnecessary_orders(open_orders, grid_levels, grid_levels[1] - grid_levels[0])
            
            # Create or maintain grid orders
            manage_grid(grid_levels, order_amount, open_orders)
            
            # Sleep for a defined interval to avoid rate limit issues
            time.sleep(time_interval)

        except Exception as e:
            logging.error(f"Exception in main loop: {e}")
            time.sleep(30)  # If there's an exception, wait before retrying

# Start the grid trading bot
grid_trading_bot()








# import ccxt
# import time
# import logging
# import time
# import dotenv
# import os


# # Set up logging to monitor bot activity and errors
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Initialize the exchange with API keys
# dotenv.load_dotenv()
# id = os.getenv("id")
# secret = os.getenv("secret" )

# exchange = ccxt.phemex({
#     'apiKey': id,
#     'secret': secret,
#     'timeout': 30000,
#     'enableRateLimit': True,
# })

# # Grid parameters
# base_asset = "BTC"
# quote_asset = "USDT"
# pair = f"{base_asset}/{quote_asset}"
# grid_size = 5  # Adjust as needed
# price_range = (30000, 35000)  # Adjust the price range as needed
# order_amount =1.1/exchange.fetch_ticker(pair)['last']  # Amount to buy/sell at each level
# time_interval = 10  # Interval to check and manage orders in seconds

# # Function to calculate grid levels
# def calculate_grid_levels(price_min, price_max, grid_size):
#     price_step = (price_max - price_min) / (grid_size - 1)
#     return [price_min + i * price_step for i in range(grid_size)]

# # Function to fetch current price
# def fetch_current_price():
#     ticker = exchange.fetch_ticker(pair)
#     return (ticker['bid'] + ticker['ask']) / 2

# # Function to fetch open orders
# def fetch_open_orders():
#     try:
#         return exchange.fetch_open_orders(pair)
#     except Exception as e:
#         logging.error(f"Error fetching open orders: {e}")
#         return []

# # Function to create or maintain the grid
# def manage_grid(grid_levels, order_amount):
#     open_orders = fetch_open_orders()

#     for level in grid_levels:
#         # Ensure there's a buy order at this grid level
#         buy_orders = [o for o in open_orders if o['side'] == 'buy' and o['price'] == level]
#         if not buy_orders:
#             try:
#                 buy_order = exchange.create_limit_buy_order(pair, order_amount, level)
#                 logging.info(f"Created new buy order at {level}: {buy_order}")
#             except Exception as e:
#                 logging.error(f"Error creating buy order at {level}: {e}")

#         # Ensure there's a sell order at the corresponding sell level
#         sell_price = level + (grid_levels[1] - grid_levels[0])  # Calculate sell price
#         sell_orders = [o for o in open_orders if o['side'] == 'sell' and o['price'] == sell_price]
#         if not sell_orders:
#             try:
#                 sell_order = exchange.create_limit_sell_order(pair, order_amount, sell_price)
#                 logging.info(f"Created new sell order at {sell_price}: {sell_order}")
#             except Exception as e:
#                 logging.error(f"Error creating sell order at {sell_price}: {e}")

# # Main loop for continuous operation
# def grid_trading_bot():
#     grid_levels = calculate_grid_levels(price_range[0], price_range[1], grid_size)
    
#     while True:
#         try:
#             current_price = fetch_current_price()
#             logging.info(f"Current price: {current_price}")
            
#             # Adjust grid levels if needed
#             manage_grid(grid_levels, order_amount)
            
#             # Sleep for a defined interval to avoid rate limit issues
#             time.sleep(time_interval)

#         except Exception as e:
#             logging.error(f"Exception in main loop: {e}")
#             time.sleep(30)  # If there's an exception, wait before retrying

# # Start the grid trading bot
# grid_trading_bot()
