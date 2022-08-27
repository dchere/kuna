class InflationIndex:

  def __init__(self):

    import datetime
    self.dt = datetime
    import requests
    self.requests = requests
    from bs4 import BeautifulSoup
    self.BS = BeautifulSoup

    self.indices = dict()
    self._get_indices_()

  def _get_indices_(self):
    """
    Requests the all available inflation indices from the minfin site
    """
    # as we could be blocked or the page could be missed
    try:

      rounded = lambda x: 0.001 * round(1000 * x)
      equal = lambda x, y: abs(x - y) < 0.001

      def number(x):
        """
        Converts content of the sell to the float or returns 1 for empty cell
        """
        x = x.get_text().replace(',','.')
        if (len(x) > 0):

          return 0.001 * int(10 * float(x))
        else:

          return False

      def _check_(year):
        """
        Checks correctness of the data reading if the year is present in the
        reference table
        """
        reference = {
          2000 : [1.258, 1.046, 1.033, 1.02,  1.017, 1.021, 1.037, .999,  1.,    1.026, 1.014, 1.004, 1.016],
          2001 : [1.061, 1.015, 1.006, 1.006, 1.015, 1.004, 1.006, .983,  .998,  1.004, 1.002, 1.005, 1.016],
          2002 : [.994,  1.01,  .986,  .993,  1.014, .997,  .982,  .985,  .998,  1.002, 1.007, 1.007, 1.014],
          2003 : [1.082, 1.015, 1.011, 1.011, 1.007, 1.,    1.001, .999,  .983,  1.006, 1.013, 1.019, 1.015],
          2004 : [1.123, 1.014, 1.004, 1.004, 1.007, 1.007, 1.007, 1.,    .999,  1.013, 1.022, 1.016, 1.024],
          2005 : [1.103, 1.017, 1.01,  1.016, 1.007, 1.006, 1.006, 1.003, 1.,    1.004, 1.009, 1.012, 1.009],
          2006 : [1.116, 1.012, 1.018, .997,  .996,  1.005, 1.001, 1.009, 1.,    1.02,  1.026, 1.018, 1.009],
          2007 : [1.166, 1.005, 1.006, 1.002, 1.,    1.006, 1.022, 1.014, 1.006, 1.022, 1.029, 1.022, 1.021],
          2008 : [1.223, 1.029, 1.027, 1.038, 1.031, 1.013, 1.008, .995,  .999,  1.011, 1.017, 1.015, 1.021],
          2009 : [1.123, 1.029, 1.015, 1.014, 1.009, 1.005, 1.011, .999,  .998,  1.008, 1.009, 1.011, 1.009],
          2010 : [1.091, 1.018, 1.019, 1.009, .997,  .994,  .996,  .998,  1.012, 1.029, 1.005, 1.003, 1.008],
          2011 : [1.046, 1.01,  1.009, 1.014, 1.013, 1.008, 1.004, .987,  .996,  1.001, 1.,    1.001, 1.002],
          2012 : [.998,  1.002, 1.002, 1.003, 1.,    .997,  .997,  .998,  .997,  1.001, 1.,    .999,  1.002],
          2013 : [1.005, 1.002, .999,  1.,    1.,    1.001, 1.,    .999,  .993,  1.,    1.004, 1.002, 1.005],
          2014 : [1.249, 1.002, 1.006, 1.022, 1.033, 1.038, 1.01,  1.004, 1.008, 1.029, 1.024, 1.019, 1.03],
          2015 : [1.433, 1.031, 1.053, 1.108, 1.14,  1.022, 1.004, .99,   .992,  1.023, .987,  1.02,  1.007],
          2016 : [1.124, 1.009, .996,  1.01,  1.035, 1.001, .998,  .999,  .997,  1.018, 1.028, 1.018, 1.009],
          2017 : [1.137, 1.011, 1.01,  1.018, 1.009, 1.013, 1.016, 1.002, .999,  1.020, 1.012, 1.009, 1.01],
          2018 : [1.098, 1.015, 1.009, 1.011, 1.008, 1.,    1.,    .993,  1.,    1.019, 1.017, 1.014, 1.008],
          2019 : [1.041, 1.01,  1.005, 1.009, 1.01,  1.007, .995,  .994,  .997,  1.007, 1.007, 1.001, .998],
          2020 : [1.05,  1.002, .997,  1.008, 1.008, 1.003, 1.002, .994,  .998,  1.005, 1.01,  1.013, 1.009],
          2021 : [1.1,   1.013, 1.01,  1.017, 1.007, 1.013, 1.002, 1.001, .998,  1.012, 1.009, 1.008, 1.006],
        }
        if year in reference.keys():

          for i in range(13):

            assert(equal(reference[year][i],self.indices[year][i]))

      full_page = self.requests.get(
        'https://index.minfin.com.ua/ua/economy/index/inflation/',
        headers={
          'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KH'\
          'TML, like Gecko) Chrome/81.0.4044.92 Safari/537.36'
          }
      )
      soup = self.BS(full_page.content, 'html.parser')
      # we expect only one table on the page
      table = soup.find_all("div", {"class": "idx-block-1120 compact-table"})
      assert(len(table) == 1)
      table = table.pop()

      rows = table.find_all("tr")
      # headers should be 14: first is blank, 12 months plus annual
      assert(14 == len(rows.pop(0).find_all("th")))

      for row in rows:
        # here should be a year and annual index
        columns = row.find_all("th")
        assert(2 == len(columns))
        year = int(columns[0].get_text())
        self.indices[year] = [number(columns[1])] + [0] * 12
        columns = row.find_all("td")
        # we expect 12 month in a year. Should we?
        assert(12 == len(columns))
        for i in range(len(columns)):
          self.indices[year][i + 1] = number(columns[i])
        # check that everything was read and sorted up correctly
        _check_(year)

        # if we need extrapolate some data TODO!
        while False in self.indices[year]:

          ind = self.indices[year].index(False)
          self.indices[year][ind] = rounded(1 + (self.indices[year][0] - 1)/(ind - 1))

          ind = 1
          for i in range(1,13):
            if self.indices[year][i]:
              ind *= self.indices[year][i]
          self.indices[year][0] = rounded(ind)
    except self.requests.exceptions.RequestException:

      return self._get_indices_()

  def inflated(self, value : float, start : int, end : int) -> float:
    """
    Groups exchange rates by month and prints them up
    """

    v = abs(value)
    # TODO: presort dates
    t0 = self.dt.datetime.utcfromtimestamp(start)
    t1 = self.dt.datetime.utcfromtimestamp(end)

    # TODO
    years = self.indices.keys()
    if (t0.year < min(years)) or (t1.year > max(years)):

      print('Could not estimate the inflation')
      return value

    # TODO: different number of digits after the point
    rounded = lambda x: .01 * round(100 * x)

    if t1.year > t0.year:

      # inflation to the end of the month
      m0 = self.dt.datetime(year=t0.year, month=t0.month, day=1)
      m1 = self.dt.datetime(year=t0.year + 1, month=1, day=1) \
        if (t0.month == 12) else \
           self.dt.datetime(year=t0.year, month=t0.month + 1, day=1)
      k = self.indices[t0.year][t0.month] - 1
      k *= (m1 - t0).total_seconds() / (m1 - m0).total_seconds()
      v = rounded((k + 1) * v)

      # to the end of the year
      for i in range(m1.month, 13):

        v = rounded(v * self.indices[t0.year][i])
      t0 = self.dt.datetime(year=t0.year + 1, month=1, day=1)

      # up to the end of the last year
      for year in range(t0.year,t1.year):

        v = rounded(v * self.indices[year][0])
      t0 = self.dt.datetime(year=t1.year, month=1, day=1)

    if t1.month > t0.month:

      # inflation to the end of the month
      m0 = self.dt.datetime(year=t0.year, month=t0.month, day=1)
      m1 = self.dt.datetime(year=t0.year, month=t0.month + 1, day=1)
      k = self.indices[t0.year][t0.month] - 1
      k *= (m1 - t0).total_seconds() / (m1 - m0).total_seconds()
      v = rounded((k + 1) * v)

      # up to the last month
      for month in range(t0.month + 1, t1.month):

        v = rounded(v * self.indices[t0.year][month])
      t0 = self.dt.datetime(year=t0.year, month=t1.month, day=1)

    # inflation between dates
    m0 = self.dt.datetime(year=t0.year, month=t0.month, day=1)
    m1 = self.dt.datetime(year=t0.year, month=t0.month + 1, day=1) \
      if (t0.month < 12) else \
         self.dt.datetime(year=t0.year + 1, month=1, day=1)
    k = self.indices[t0.year][t0.month] - 1
    k *= (t1 - t0).total_seconds() / (m1 - m0).total_seconds()
    v = rounded((k + 1) * v)

    if value < 0:
      v = rounded(value + v - rounded(-1 * value))
      if v > 0:
        v = 0
    return v
