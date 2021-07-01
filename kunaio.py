import requests
import hashlib
import random
import time
import json
import hmac

DOMAIN = "https://api.kuna.io/v3/"

def get_server_time():
  """
  Get actual server time.

  Returns:
    (dict): {
      "timestamp"             (int) : in Unix format
      "timestamp_miliseconds" (int) : the same but with higher precision
    }
  """

  return _request("timestamp")

def get_timestamp():
  """
  Get actual server time. The same as get_server_time().

  Returns:
    (dict): {
      "timestamp"             (int) : in Unix format
      "timestamp_miliseconds" (int) : the same but with higher precision
    }
  """

  return get_server_time()

def get_currencies_list():
  """
  Get list of all available currencies on the market.

  Returns:
    (list): [
      {
        "id"            (int)       : internal (kuna.io) ID of the currency
        "code"          (str)       : short name (ISO) of the currency
        "name"          (str)       : full name of the currency
        "has_memo"      (bool)      : is Memo required for the currency
        "icons"         (dict)      : {
          "std"     (str) : URL,
          "xl"      (str) : URL,
          "png_2x"  (str) : URL,
          "png_3x"  (str) : URL
        },
        "coin"          (bool)      : is the currency a сryptocurrency
        "explorer_link" (str)       : template of a link for TXID in an explorer
                        (NoneType)  : if not applicable,
        "sort_order"    (int)       : position in the sort (?)
        "precision"     (dict)      : {
          "real"  : int,
          "trade" : int
        },
        privileged      (bool)      : ?
        fuel            (bool)      :
                        (NoneType)  : if not applicable
      },
    ]
  """

  return _request("currencies")

def get_markets_list():
  """
  Get list of all available currency exchange markets.

  Returns:
    (list): [
      {
        "id"                (str)   : ticker for a currency pair
        "base_unit"         (str)   : base currency short name
        "quote_unit"        (str)   : quoted currency short name
        "base_precision"    (int)   : rounding precision of the base currency
        "quote_precision"   (int)   : rounding precision of the quoted currency
        "display_precision" (int)   : precision for the orders grouping in the
                                      order book
        "price_change"      (float) : price changing (in %) comparing to the
                                      same moment 24 hours ago
      },
    ]
  """

  return _request("markets")

def get_recent_market_data(ticker="ALL"):
  """
  Get recent market data.

  Optional arguments:
    ticker (str): the currency pair name.
  or
    list["str"]: the names of currency pairs.
  or
    default behavior: all available pairs on the market.

  Returns:
    (list): [
      (list): [
        [0]  (str)   ticker of the market,
        [1]  (float) bid price,
        [2]  (float) volume of the bid order book,
        [3]  (float) ask price,
        [4]  (float) volume of the ask order book,
        [5]  (float) change of the price comparing to the same moment 24 hours
                     ago in a quoted currency,
        [6]  (float) change of the price comparing to the same moment 24 hours
                     ago in percents
        [7]  (float) last deal price
        [8]  (float) total volume of all deals during the past 24 hours in a
                     base currency
        [9]  (float) maximum price during the last 24 hours
        [10] (float) minimum price during the last 24 hours
      ]
    ]
  """

  if isinstance(ticker, str):
    args = {"symbols": ticker}
  elif isinstance(ticker, list):
    args = {"symbols": ",".join(ticker)}
  else:
    args = {"symbols": "ALL"}

  return _request("tickers", args=args)

def get_order_book(ticker):
  """
  Get order book.

  Args:
    ticker (str): the market name.

  Returns:
    (list): [
      (list): [
        (float) price,
        (float) volume (>0 for Bid, <0 for Ask),
        (float) amount of positions
      ]
    ]
  """

  return _request(f"book/{ticker}")

def get_fees():
  """
  List of active methods to put in/out currencies, and commissions.

  Returns:
    (list): [
      (dict) {
        "code"          (str)   : method of a withdraw for a fiat currency.
                                  Possible variants:
                                    "advcash_wallet", "payeer", "payment_card",
                                    "perfectmoney_account",
                                    "perfectmoney_transfer", "kuna_code"
                                  symbol of a сryptocurrency
        "category"      (str)   : symbol of a fiat currency
                                : always "coin" for a сryptocurrency
        "currency"      (str)
        "deposit_fees"  (dict)  : ?
        "withdraw_fees" (str) : ?
      }
    ]
  """

  return _request("fees")

def get_user_info(keys):
  """
  Returns an account data that is owner of yours keys.

  Arguments:
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Returns:
    (dict): {
      "email"                 (str)   : email address,
      "kunaid"                (str)   : id of the user in the Kuna system,
      "two_factor"            (bool)  : is Two-factor Authentication enabled,
      "withdraw_confirmation" (bool)  : ,
      "send_order_notice"     (bool)  : ,
      "newsletter"            (bool)  : ,
      "send_withdraw_notice"  (bool)  : ,
      "send_signin_notice"    (bool)  : ,
      "public_keys"           (dict) : {
        "deposit_sdk_uah_public_key" (str) : ,
        "deposit_sdk_usd_public_key" (str) : ,
        "deposit_sdk_rub_public_key" (str) : ,
        "deposit_sdk_uah_worldwide_public_key" (str):
      },
      "announcements"         (bool)  : ,
      "sn"                    (str)   : ,
      "activated"             (bool)  : ,
      "verifications"         (dict) : {
        "status"    (str)       : ,
        "identity"  (NoneType)  : ,
      }
    }
  """

  return _request("auth/me", keys=keys)

def get_user_balance(keys):
  """
  Return balances and accessible funds on all available user"s wallets.

  Arguments:
    keys (dict): {
      "privat" : "",
      "public" : ""
    }

  Returns:
    (list) [
      (list) [
        [0] (str)       : "exchange",
        [1] (str)       : short name of the currency,
        [2[ (float)     : total balance,
        [3] (NoneType)  : not in use,
        [4] (float)     : accessible amount
      ],
    ]
  """

  return _request("auth/r/wallets", keys=keys)

def request_email_user_history(market, keys, date_from=None, date_to=None):
  """
  Requests an email with trade history of a market in csv format.

  Arguments:
    ticker (str) : market name
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Optional arguments:
    date_from (int) : time stamp in Unix format,
    date_to (int) : time stamp in Unix format,
  """

  body = {"market": market.lower(),}
  if date_from:
    body["date_from"] = date_from
  if date_to:
    body["date_to"] = date_to

  _request("auth/history/trades", body=body, keys=keys)

def get_user_active(keys, market=None):
  """
  List of the user"s active orders.

  Arguments:
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Optional arguments:
    market (str) : name of a market

  Returns:
    (list) [
      (list) [
        [0]   (int)       order ID,
        [1]   (NoneType)  not in use,
        [2]   (NoneType)  not in use,
        [3]   (str)       market name,
        [4]   (int)       time stamp of the creation in ms,
        [5]   (int)       time stamp of the update in ms,
        [6]   (str)       volume of the order,
        [7]   (str)       initial volume of the order, positive means BUY,
        [8]   (str)       order type "LIMIT" or "MARKET",
        [9]   (NoneType)  not in use,
        [10]  (NoneType)  not in use,
        [11]  (NoneType)  not in use,
        [12]  (NoneType)  not in use,
        [13]  (str)       order status,
        [14]  (NoneType)  not in use,
        [15]  (NoneType)  not in use,
        [16[  (str)       order price,
        [17]  (str)       average price of deals in the order,
        [18]  (NoneType)  not in use,
        [19]  (NoneType)  not in use,
        [20]  (NoneType)  not in use,
        [21]  (NoneType)  not in use,
        [22]  (NoneType)  not in use,
        [23]  (NoneType)  not in use,
        [24]  (NoneType)  not in use
      ],
    ]
  """

  S = f"auth/r/orders/{market}" if market else "auth/r/orders"
  return _request(S, keys=keys)

def get_user_executed(keys, market=None, start=None, end=None, limit=None, sort=None):
  """
  List of the user"s executed orders.

  Arguments:
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Optional arguments:
    market (str) : name of a market,
    start (int) : date from in ms. By default 2 weeks ago,
    end (int) : date to in ms. By default now,
    limit (int) : amount of orders. By default 25. Max 100,
    sort (int) : 1 or -1. Sort order. By default in descending order,

  Returns:
    (list) [
      (list) [
        [0]  (int)      order ID,
        [1]  (NoneType) not in use,
        [2]  (NoneType) not in use,
        [3]  (str)      market name,
        [4]  (int)      time stamp of the creation in ms,
        [5]  (int)      time stamp of the update in ms,
        [6]  (str)      volume of the order,
        [7]  (str)      initial volume of the order, positive means BUY,
        [8]  (str)      order type "LIMIT" or "MARKET",
        [9]  (NoneType) not in use,
        [10] (NoneType) not in use,
        [11] (NoneType) not in use,
        [12] (NoneType) not in use,
        [13] (str)      order status,
        [14] (NoneType) not in use,
        [15] (NoneType) not in use,
        [16] (str)      order price,
        [17] (str)      average price of deals in the order,
        [18] (NoneType) not in use,
        [19] (NoneType) not in use,
        [20] (NoneType) not in use,
        [21] (NoneType) not in use,
        [22] (NoneType) not in use,
        [23] (NoneType) not in use,
        [24] (NoneType) not in use
      ],
    ]
  """

  body = {}
  if start:
    body["start"] = start
  if end:
    body["end"] = end
  if limit:
    body["limit"] = limit
  if sort:
    body["sort"] = sort
  path = f"auth/r/orders/{market + '/' if market else ''}hist"
  if start:
    body["start"] = start

  return _request(path, body=body, keys=keys)

def get_order_details(market, order_id, keys):
  """
  List of dealings for a certain order

  Arguments:
    market (str) : market name
    order_id (int) : order id
    keys (dict): {
      "private" : "",
      "public" : ""
    }


  Returns:
    (list)  [
      (list)  [
        [0]   (int)       ID of the deal,
        [1]   (str)       market name,
        [2]   (int)       [ms] deal time,
        [3]   (int)       order ID,
        [4]   (str)       volume of the deal,
        [5]   (str)       price of the deal,
        [6]   (NoneType)  not in use,
        [7]   (NoneType)  not in use,
        [8]   (int)       1 if maker, -1 if taker,
        [9]   (str)       volume of the commission,
        [10]  (str)       currency of the commission
      ],
    ]
  """

  S = f"auth/r/order/{market}:{order_id}/trades"
  return _request(S, keys=keys)

def set_order(market, order_type, amount, price, keys, stop_price=None):
  """
  Create an order

  Arguments:
    market (str) : market name,
    order_type (str) : may be "limit", "market", "market_by_quote",
                       "limit_stop_loss"
    amount (float) : positive if BUY order, and negative for SELL
    price (float) : price of 1 ask currency in a quoted currency. Necessary only
                    when type is "limit"
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Optional arguments:
    stop_price (float) : price when activates "limit_stop_loss" type order. If
                         None then the same as price

  Returns:
    (list) [
      [0]   (int)       order ID,
      [1]   (NoneType)  not in use,
      [2]   (NoneType)  not in use,
      [3]   (str)       name of the market,
      [4]   (int)       time stamp of the creation in ms,
      [5]   (int)       time stamp of the update in ms,
      [6]   (str)       initial volume,
      [7]   (str)       order volume,
      [8]   (str)       order type ("LIMIT" or "MARKET"),
      [9]   (NoneType)  not in use,
      [10]  (NoneType)  not in use,
      [11]  (NoneType)  not in use,
      [12]  (NoneType)  not in use,
      [13]  (str)       order status,
      [14]  (NoneType)  not in use,
      [15]  (NoneType)  not in use,
      [16]  (str)       order price,
      [17]  (str)       average price of deals in order,
      [18]  (NoneType)  not is use,
      [19]  (str)       for stop price but None for other orders,
      [20]  (NoneType)  not in use,
      [21]  (NoneType)  not in use,
      [22]  (NoneType)  not in use,
      [23]  (NoneType)  not in use,
      [24]  (NoneType)  not in use,
      [25]  (NoneType)  not in use,
      [26]  (NoneType)  not in use,
      [27]  (NoneType)  not in use,
      [28]  (NoneType)  not in use,
      [29]  (NoneType)  not in use,
      [30]  (NoneType)  not in use,
      [31]  (NoneType)  not in use,
    ]
  """
  body = {
    "symbol": market,
    "type": order_type,
    "amount": amount,
    "price": price,
    "stop_price": price,
  }

  return _request("auth/w/order/submit", body=body, keys=keys)

def cancel_order(order_id, keys):
  """
  Cancel the order

  Arguments:
    order_id (int) : ID of the order
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Returns:
    (dict) {
      "id"                  (int) : order ID,
      "side"                (str) : "buy" or "sell",
      "type"                (str) : type of the order ("limit"),
      "price"               (str) : price,
      "avg_execution_price" (str) : average price of the order execution,
      "state"               (str) : state,
      "symbol"              (str) : market name,
      "timestamp"           (int) : time stamp,
      "original_amount"     (str) : initial amount,
      "remaining_amount"    (str) : remaining amount,
      "executed_amount"     (str) : executed amount,
      "is_cancelled"              : None,
      "is_hidden"                 : None,
      "is_live"                   : None,
      "was_forced"                : None,
      "exchange"                  : None
    }
  """
  body = {"order_id": order_id}

  return _request("order/cancel", body=body, keys=keys)

def http_test(keys):
  """
  Test HTTP connection to private API

  Arguments:
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Returns: empty dict. Main idea do not catch and error
  """

  return _request("http_test", keys=keys)

def _request(path, args={}, body={}, keys=None, iteration=1):
  """
  Fetches the given path in the Kuna API.

  Arguments:
    path (str) : API path
    args (dict): arguments for a GET request
    body (dict): body of a POST request

  Optional arguments:
    keys (dict): {
      "private" : "",
      "public" : ""
    }

  Returns: serialized server's response
  """
  def _getUserAgent():

    uas = [
      "{}4.24{}) Chrome/11.0.696.3 Safari/534.24",
      "{}7.36{}; Google Web Preview) Chrome/27.0.1453 Safari/537.36",
      "{}7.36{}; Google Web Preview) Chrome/41.0.2272.118 Safari/537.36",
      "{}7.36{}) Chrome/42.0.2311.135 Safari/537.36",
      "{}7.36{}) Chrome/44.0.2403.157 Safari/537.36",
      "{}7.36{}) Chrome/60.0.3112.101 Safari/537.36",
      "{}7.36{}) Chrome/64.0.3282.24 Safari/537.36",
      "{}7.36{}) Chrome/69.0.3497.12 Safari/537.36",
      "{}7.36{}) Chrome/72.0.3626.121 Safari/537.36",
      "{}7.36{}) Chrome/76.0.3809.132 Safari/537.36",
      "{}7.36{}) Chrome/77.0.3865.120 Safari/537.36",
      "{}7.36{}) Chrome/80.0.3987.87 Safari/537.36",
      "{}7.36{}) Chrome/81.0.4044.92 Safari/537.36",
    ]
    return uas[int(len(uas)*random.random())].format(
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53",
      " (KHTML, like Gecko"
    )

  try:

    headers = {
      "accept" : "application/json",
      "user-agent" : _getUserAgent(),
    }
    # if it is not private method
    if not keys:

      # in case of absent arguments it will be OK for the requests
      return requests.get(DOMAIN+path, data=args, headers=headers).json()

    # according to the documentation
    if body:

      headers["content-type"] = "application/json"
    jbody = json.dumps(body)

    # here keys are always present so the method is always private
    nonce = str(int(time.time() * 1000))
    headers["kun-nonce"] = nonce
    headers["kun-apikey"] = keys["public"]
    headers["kun-signature"] = hmac.new(
      keys["private"].encode("ascii"),
      f"{DOMAIN[-4:]}{path}{nonce}{jbody}".encode("ascii"),
      hashlib.sha384
    ).hexdigest()

    return requests.post(DOMAIN+path, data=jbody.encode(), headers=headers).json()
  except Exception as e:

    print(f"{e}. But we will try again. Failed on the iteration #{iteration}.")
    return _request(path=path, args=args, body=body, keys=keys, iteration=iteration+1)
