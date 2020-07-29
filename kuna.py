
import os
import time
import requests

import numpy as np
import pandas as pd

SECONDS_IN_A_WEEK = 604800
"""int: number of seconds in a week. Used for storing and forecasting interval
specification"""

def deltatime(time):
  """
  Helper function that generates a difference in seconds between the deal moment
  and the start of 01.01.2020 day

    Args:
      time (str): current time in format 'YYYY-MM-DDTHH:MM:SSZ'

    Returns:
      float: seconds of difference between two dates
  """

  def leap_year(Y):
    """
    Helper function to decide is the year is a leap year or not

      Args:
        Y (int): year

      Returns:
        bool: True if it is a leap year and False in the other case
    """
    return True if ((Y%400==0) or ((Y%4==0) and (Y%100!=0))) else False

  Sum = 0
  year = int(time[:4])
  for Year in range(2020, year):
    Sum += 366 if leap_year(Year) else 365
  month = int(time[5:7])
  for Month in range(1, month):
    if (month == 2):
      Sum += 29 if leap_year(year) else 28
    elif (month in [1, 3, 5, 7, 8, 10, 12]):
      Sum += 31
    else:
      Sum += 30
  Sum += int(time[8:10]) - 1
  Sum *= 86400
  Sum += 3600*int(time[-9:-7])
  Sum += 60*int(time[-6:-4])
  Sum += int(time[-3:-1])
  return Sum

class Coins:
  """ Main class that provides communication with server and the storage """

  domain = 'https://kuna.io'
  path = '/api/v2/'

  def get_server_time(self):
    """
    Get server time.

    Returns:
      int: time stamp in Unix format
    """
    return self.request('timestamp')

  def get_recent_market_data(self, ticker):
    """
    Get recent market data.

    Args:
      ticker (str): the coins pair name.

    Returns:
      dict: dictionary with recent data for the picked up pair
    """
    return self.request('tickers/%s'%ticker)

  def get_order_book(self, ticker):
    """
    Get actual list of orders.

    Args:
      ticker (str): the market name.

    Returns:
      dict: dictionary with recent orders for a selected coins pair
    """
    return self.request('depth?market=%s'%ticker)

  def get_active_user_orders(self, ticker):
    """
    User method. Get actual list of user's orders.

    Args:
      ticker (str): the market name.

    Returns:
      dict: dictionary with recent orders for a selected coins pair
    """
    return self.request(
      'orders',
      args={'market': self.ticker},
      is_user_method=True
    )

  def place_order(self, side, volume, ticker, price):
    """
    User method. Void method that places an order to the order list.

    Args:
      side (str): buy or sell.
      volume (float): volume of the order in BTC? TODO
      ticker (str): the market name
      price (float): price for 1 BTC? TODO
    """
    self.request(
      'orders',
      args={
        'side': side,
        'volume': volume,
        'market': ticker,
        'price': price
      },
      method='POST',
      is_user_method=True
    )

  def cancel_order(self, order_id):
    """
    User method. Void method that cancels the order by ID.

    Args:
      order_id (int): Id of the order.
    """
    self.request(
      'order/delete',
      args={'id': order_id},
      method='POST',
      is_user_method=True
    )

  def get_trades_history(self, ticker):
    """
    Get trades history for the coins pair

    Args:
      ticker (str): the market name

    Returns:
      dict: dictionary with recent history of executed orders.
    """
    return self.request('trades?market=%s'%ticker)

  def get_user_trade_history(self, ticker):
    """
    User method. Get user's trade history.

    Args:
      ticker (str): the market name.

    Returns:
      dict: dictionary of executed user's orders for the current coins pair.
    """
    return self.request(
      'trades/my',
      args={'market': ticker},
      is_user_method=True
    )

  def get_user_account_info(self):
    """
    User method. Get information about the user and his assets.

    Returns:
      dict: dictionary with user data and assets.
    """
    return self.request('members/me', is_user_method=True)

  def get_file_name(self, ticker):
    """
    Helper function. Returns the file name where the history is stored.

    Args:
      ticker (str): the coins pair name.

    Returns:
      str: file name string.
    """
    return ('%s.csv' % ticker)

  def request(self, path, args={}, method='GET', is_user_method=False):
    """
    Helper method that service all request to the Kuna server.

    Args:
      path (str): request string without domain.
      args (dict): dictionary of arguments. Void by default.
        'market' field is the market name;
        'side' is buy or sell type of the order;
        'volume' volume of the order;
        'price': price for 1 coin in the order;
        'id': Id of the order;
        'access key', 'tonce' and 'signature' will be auto-generated for the
        user methods.
      method (str): Method of the request. POST or GET. GET is the default.
      is_user_method (bool): boolean flag to separate general requests from
      those which depends on the user's info.

    Returns:
    dict: dictionary that is the response to the request.
    """
    if is_user_method:
      args['access_key'] = self.access_key
      args['tonce'] = int(time.time() * 1000) # current time in ms
      args['signature'] = self.generate_signature(method, path, args)

    try:
      response = requests.request(
        method,
        self.domain + self.path + path,
        params=args
      )
      return response.json()
    except:
      return {}

  def generate_signature(self, method, path, args):
    """
    Helper method that generates signature by an algorithm
    HEX(HMAC-SHA256("HTTP-verb|URI|params", secret_key)) to service the user
    methods.

    Args:
      method (str): POST or GET.
      path (str): request string without domain.
      args (dict): dictionary of arguments.

    Returns:
      str: string signature.
    """
    # HTTP-verb
    msg = method
    # URI
    msg += '|' + self.path + path
    # parameters
    msg += '|' + urlencode(sorted(args.items(), key=lambda val: val[0]))
    msg = msg.encode('ascii')
    return hmac.new(self.secret_key, msg, hashlib.sha256).hexdigest()

  def idle(self):
    """
    Void method that provides an idle mode.
    """
    def ctime():
      """
      Helper function to get current time.

      Returns:
        int: current time
      """
      return int(0.5 + time.time())

    time_delta = 60 # s, minimal duration between requests
    time_last = ctime() # s, moment of the last request

    # infinite loop to provide idle mode
    while True:
      # How many seconds until the next response
      delta = time_delta - (ctime() - time_last) - 1
      # If we have some free time we will be dancing in the background mode
      if delta > 0:
        print('%s | Sleep for %d seconds' %
          (time.strftime("%H:%M:%S", time.localtime()), delta))
        time.sleep(delta)
      time_last = ctime()
      # Collect statistic
      self.update_rates()
      if True in list(self.newData.values()):
        for key in list(self.rates):
          if self.newData[key]:
            self.newData[key] = False
            self.reduce_rates(key)
            self.write_rates(key)

  def reduce_rates(self, key):
    """
    Reduce all transactions those are older than 3 weeks
    """
    IDs = list(self.rates[key])
    IDs.sort()
    first_deal_time = self.rates[key][IDs[-1]]['time'] - 3*SECONDS_IN_A_WEEK
    for i in range(len(IDs)):
      if (self.rates[key][IDs[i]]['time'] >= first_deal_time):
        break
      else:
        del self.rates[key][IDs[i]]

  def read_rates(self):
    """
    Void helper method that reads stored rates from the relevant files. Void
    because we keep that information in the memory during the script execution.
    """
    # for each coins pair from the list of interest
    for key in list(self.rates):
      # file name where exchange rates are stored
      fileName = self.get_file_name(key)
      # if exist
      if os.path.isfile(fileName):
        # read from the file
        df = pd.read_csv(fileName)
        # takes the list of ids from the dataset
        IDs = list(df.loc[:,'id'])
        # pull relevant data to the dictionary
        for i in range(len(IDs)):
          self.rates[key][IDs[i]] = {
            'price':df.loc[i,'price'],
            'volume':df.loc[i,'volume'],
            'funds':df.loc[i,'funds'],
            'time':df.loc[i,'time'],
            'trend':df.loc[i,'trend'],
          }
        # a brief feedback message
        print('Rates were read from the %s' % fileName)

  def write_rates(self, ticker):
    """
    Void helper method that stores rates to the relevant files.
    :param 'ticker': coins pair name.
    """
    # if there at least one item in the dictionary
    if (len(self.rates[ticker]) > 0):
      rates = []
      for ID in list(self.rates[ticker]):
        rates.append([
          ID,
          self.rates[ticker][ID]['price'],
          self.rates[ticker][ID]['volume'],
          self.rates[ticker][ID]['funds'],
          self.rates[ticker][ID]['time'],
          self.rates[ticker][ID]['trend']
        ])
      # pandas services to write an csv file
      pd.DataFrame( np.array(rates),
        columns=['id', 'price', 'volume', 'funds', 'time', 'trend']
      ).to_csv(self.get_file_name(ticker), sep=',')
    # a brief feedback message
    print('%d orders of %s were written to the file'%(len(rates),ticker))

  def update_list(self):
    """
    Void helper method that check all tickers on the server and collect all
    coins those are pair to the UAH.
    """
    tickers = self.request('tickers')
    self.rates = {}
    self.newData = {}
    for ticker in list(tickers):
      if (ticker[-3:] == 'uah') and (not ticker == 'remuah'):
        self.rates[ticker] = {}
        self.newData[ticker] = False

  def update_rates(self):
    """
    Void helper method that check all pairs of coin/UAH from the list of
    interest by the latest order book from the Kuna server.
    """
    # for all coins from the list of interest
    for key in list(self.rates):
      # requests the order book
      content = self.get_trades_history(key)
      # for each order in the order book
      for deal in content:
        ID = deal['id']
        # if we do not have info about the order
        if not ID in list(self.rates[key]):
          # new data in the dictionary
          self.newData[key] = True
          self.rates[key][ID] = {
            'price':float(deal['price']),
            'volume':float(deal['volume']),
            'funds':float(deal['funds']),
            'time':deltatime(deal['created_at']),
            'trend':deal['trend']
          }

  def __init__(self):
    self.update_list()
    self.read_rates()
    self.update_rates()

coins = Coins()
coins.idle()