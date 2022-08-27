class ExchangeRate:

  def __init__(self, currencies={'USD'}, fromDate=202202240455):

    import datetime
    import requests
    from bs4 import BeautifulSoup
    self.dt = datetime
    self.requests = requests
    self.BS = BeautifulSoup

    self.fromDate = self.dt.date(year=2022, month=2, day=24)
    self.previousDate = self.fromDate - self.dt.timedelta(days=1)
    self.currencies = dict()
    for currency in currencies:
      self.currencies[currency.upper()] = set()
    # self.update_exchange_rates()

  def get_current_rate(self):

    today = self.dt.date.today()
    if self.previousDate != today:

      rates = None
      while True:
        rates = self.get_exchange_rates(today)
        flag = len(rates) > 0
        # as we do not allowed divide by 0
        for value in rates.values():
          if value == 0:
            flag = False
            break
        if flag:
          break

      # average exchange rate where each currency represented by the same value
      # exchange_rate = amount_exchange_rates / Sum(1/exchange_rate_i)
      self.currentRate = 0
      for currency in rates.keys():

        self.currentRate += 1 / rates[currency]

      self.currentRate = len(rates.keys()) / self.currentRate
      self.currentRate = round(self.currentRate, 4)
      self.previousDate = today

    return self.currentRate

  def update_exchange_rates(self):
    """
    Checks all past days from the start of the year up to yesterday and, if the
    data for the date is not present, requests it on the NBU website.
    """

    day = self.dt.timedelta(days=1)
    today = self.dt.date.today()
    while today > self.previousDate:
      self.previousDate += day
      while True:
        rates = self.get_exchange_rates(date=self.previousDate)
        if len(rates) == len(self.currencies.keys()):
          for currency in rates.keys():
            self.currencies[currency].add(rates[currency])
          print(f'Exchange rates for {self.previousDate} were updated')
          break
    print(self.currencies)

  def get_exchange_rates(self, date):
    """
    Requests the NBU website for a echange rates on the date. Parse it and add
    to the dictionary

    Args:
      str: date of interest
    """
    # string template for website address
    date = '%02d.%02d.%04d'%(date.day, date.month, date.year)
    NBU = f'https://bank.gov.ua/markets/exchangerates?date={date}&period=daily'
    # a web browser signature for a successful request
    header = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like '\
             'Gecko) Chrome/81.0.4044.92 Safari/537.36'
    # as we could be blocked or the page could be missed
    try:

      rates = dict()
      full_page = self.requests.get(NBU, headers={'User-Agent':header})
      soup = self.BS(full_page.content, 'html.parser')
      table = soup.find_all("table")
      if (len(table) > 0):
        table = table[0]
        for row in table.find_all("tr"):
          code = row.findAll("td",{"data-label": "Код літерний"})
          if (len(code) > 0):
            code = code[0].get_text()
            if code in self.currencies.keys():
              quantity = row.findAll("td",
                                    {"data-label":"Кількість одиниць валюти"})
              quantity = float(quantity[0].get_text())
              # cost
              erate = row.findAll("td",{"data-label": "Офіційний курс"})[0]
              erate = float(erate.get_text().replace(",","."))
              # exchange rate
              rates[code] = erate/quantity
      return rates
    except self.requests.exceptions.RequestException:
      return {}

  def group_by_month(self):
    """
    Groups exchange rates by month and prints them up
    """
    # current month and year numbers
    last_day, last_month, last_year = parse_date(get_current_date())
    if (last_day == 1) and (last_month == 1):
      last_month = 12
      last_year -= 1
    for currencyName in list(self.rates):
      # to print the currency name in work
      print(currencyName)
      rates = self.rates[currencyName]
      List = list(rates)
      # for each month up to current
      for m in range(1,last_month+1):
        # to average exchange rates
        N, S = 0, 0
        # for each day
        for d in range(1,32):
          date = get_date(d, m, last_year)
          # if present
          if date in List:
            N += 1
            S += rates[date]
        # print out averaged rates
        if (N > 0):
          print("%d: %.4f"% (m, 0.0001*float(0.5 + 10000*S/N)))