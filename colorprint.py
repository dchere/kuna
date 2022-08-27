import time

class colorPrint:

  ENDC = '\033[0m'

  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

  FAIL = '\033[91m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  OKBLUE = '\033[94m'
  HEADER = '\033[95m'
  OKCYAN = '\033[96m'

  def __init__(self, number_of_columns=1):

    self.number_of_columns = number_of_columns
    self.adjust()

  def adjust(self, number_of_columns=1):

    self.number_of_columns = max(number_of_columns, self.number_of_columns)
    self.columnWidth = 13
    self.totalWidth = 2 + self.number_of_columns*(self.columnWidth + 1) - 1
    self.TAB = ' '*int(0.5 * (101 - self.totalWidth))

  def line(self, columns, align='center'):

    res = self.TAB + '|'
    while len(columns) < self.number_of_columns:
      columns += ['']
    for i in range(len(columns)):

      if (align=='center'):

        res += '{:{align}{width}}'.format(
            columns[i],
            width=self.columnWidth,
            align='^'
          )[:self.columnWidth]+'|'
      else:

        res += '{:{align}{width}}'.format(
            columns[i],
            width=self.columnWidth-1,
            align='>'
          )[:self.columnWidth-1]+' |'
    return res

  def header(self, columns):

    self.adjust(number_of_columns=len(columns))
    print(self.TAB + f"{self.BOLD}{self.HEADER}{'-'*self.totalWidth}")
    print(self.line(columns).upper())
    print(self.TAB + f"{'-'*self.totalWidth}{self.ENDC}")

  def white(self, columns):

    if type(columns) is list:

      print(self.line(columns,align='right'))
    else:

      print(columns)

  def red(self, columns):

    if type(columns) is list:

      print(f"{self.FAIL}{self.line(columns,align='right')}{self.ENDC}")
    else:

      print(f"{self.FAIL}{columns}{self.ENDC}")

  def green(self, columns):

    if type(columns) is list:

      print(f"{self.OKGREEN}{self.line(columns,align='right')}{self.ENDC}")
    else:

      print(f"{self.OKGREEN}{columns}{self.ENDC}")

  def warning(self, text):

    print(f"{self.WARNING}{text}{self.ENDC}")

  def info(self, text, silent=False, prefix='...'):

    if len(prefix)>0:
      prefix=f"{prefix.upper()}: "
    if not silent:
      print(f'{time.strftime("%H:%M:%S", time.localtime())} | {prefix}{text}')