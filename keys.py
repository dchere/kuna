import os
import sys
import random
import string
import getpass
# requires pip3 install pycrypto
from Crypto.Cipher import AES

_PATH_TO_THE_FILE_ = ".key"
"""str: path to the file with stored keys"""
_STRING_LENGTH_ = 64
"""int: number of chars in a string"""
_BLOCK_LENGTH_ = 8
"""int: length of a block that code an int"""
_MAX_LENGTH_ = 3
"""int: maximum length of an int"""

def get_input(field_name):
  """
  Requests an input and its repetition. Check the correctness.

    Args:
      s (str): name of the requesting input.

    Returns:
      str: input sting
  """

  def check_input(s):
    """
    Helper function that checks the minimum length of the string and terminates
    the program on a request.

      Args:
        s (str): input string

      Returns:
        str: string that contains at least 2 symbols.
    """

    if (len(s) == 0):

      print('You typed nothing')
      return ''
    elif (len(s) == 1):

      if (s == "X") or (s == "x"):

        sys.exit('User terminated program')
      else:

        print('You typed: ', s)
      return ''
    else:

      return s

  print('To exit just enter "X" or "x".')

  # password
  _in = ''
  # request a password and repetition
  try:

    while (len(_in) < 2):
      _in = check_input(getpass.getpass(f'Please enter a {field_name}: '))
  except Exception as error:

    print(f'Error during the {field_name} requesting: ', error)
  else:

    check = ''
    while (check != _in):

      check = check_input(getpass.getpass(f'Please repeat the {field_name}: '))

  return _in

def get_pass():
  """
  Requests a password and its repetition. Check the correctness and minimal
  length of the password. Returns 16 symbols in a binary encoding.

    Returns:
      bytes: 16 symbols length bytearray.
  """

  # password
  pswd = get_input('password')

  # if the string is not binary
  if ('encode' in dir(pswd)): pswd = pswd.encode()
  while (len(pswd) < 16): pswd += pswd[::-1]

  return pswd[:16]

def write_keys():
  """
  Encode and write keys to the file.
  """

  def get_a_char():
    """
    Helper function that returns a printable char.

      Returns:
        str: one printable char.
    """

    return string.printable[random.randint(0, 62)]

  def get_a_byte():
    """
    Returns a byte.

      Returns:
        bytes: single byte.
    """

    return get_a_char().encode()

  def form_byte_string(length):
    """
    Forms a random byte string with required length.

      Args:
        length (int): length of the string

      Returns:
        bytes: random bytearray of required length.
    """

    s = b''
    while len(s) < length:

      s += get_a_byte()
    return s

  def hide_int(number, max_length=_MAX_LENGTH_, block_length=_BLOCK_LENGTH_):
    """
    Forms a byte string of required length that stores the number in a random
    symbols.

      Args:
        number (int): number that we should store
        max_length (int): optional parameter that changes the length of the
                          mindful block
        block_length (int): optional parameter that means the length of the
                            number block in the mindful block

      Returns:
        bytes: bytearray with stored number.
    """

    # form the string
    result = '%d' % number

    # adds arbitrary zeros to the head to form a sting with required length
    while len(result) < max_length: result = '0' + result

    # adds arbitrary symbols to the head to form a block of required length
    for i in range(block_length - max_length): result += get_a_char()

    # mirrors and makes binary
    result = result[::-1].encode()

    # adds arbitrary symbols to fulfill the string
    result += form_byte_string(_STRING_LENGTH_ - len(result))

    return result

  def form_length(s):
    """
    Helper function that hides length of a string.

      Args:
        s (str): string.

      Returns:
        bytes: bytearray with a hided length of the string.
    """

    return hide_int(len(s))

  def write_block(f, msg):
    """
    Write a message as a sequence of hided integer numbers.

      Args:
        f (file): file opened for write of append bite strings
        msg (str): message to hide

      Returns:
        bytes: bytearray with stored number.
    """
    # writes length
    f.write(b'%s\n'%form_length(msg))

    # writes the message
    for symbol in msg: f.write(b'%s\n'%hide_int(symbol))

  def form_a_message():
    """
    Form a message to store from public and private keys.

      Returns:
        str: string with stored number.
    """

    pub = get_input('public key')
    pri = get_input('private key')

    # result string
    result = ''
    # mesh up two keys and adjust their length to the biggest one
    for i in range(max([len(pub), len(pri)])):
      result += pub[i] if (i < len(pub)) else get_a_char()
      result += pri[i] if (i < len(pri)) else get_a_char()
    # adds length of the public key to the front
    result = hide_int(len(pub))[:_BLOCK_LENGTH_].decode() + result
    # adds length of the private key to the back
    result += hide_int(len(pri))[:_BLOCK_LENGTH_].decode()

    return result

  # creates a file where the key will be written
  file_out = open(_PATH_TO_THE_FILE_, "wb")

  # create an initialization vector
  IV = form_byte_string(AES.block_size)
  # and store it
  write_block(file_out, IV)

  # creates cipher
  cipher = AES.new(get_pass(), AES.MODE_CFB, IV)
  # and write the message
  write_block(file_out, cipher.encrypt(form_a_message().encode()))

  print('Keys were written')

def load_keys():
  """
  Restore public and private keys from the file.

    Returns:
      dict: dictionary with restored public and private keys.
  """

  def parse_line(s):
    """
    Helper function to parse a line.

      Args:
        s (str): input string.

      Returns:
        int: number stored in the line.
    """

    result = s[_BLOCK_LENGTH_-_MAX_LENGTH_:_BLOCK_LENGTH_]
    return int(result[::-1])

  def get_a_byte(c):
    """
    Helper function to cast a byte from int.

      Returns:
        dict: dictionary with restored public and private keys.
    """

    return bytes([c])

  def parse_block(f):
    """
    Restore a byte string from the block.

    Args:
      f (file): input file opened for a read of binary data

    Returns:
      bytes: stored bytearray.
    """

    # result string
    result = b''
    # amount of lines in the block
    count = parse_line(file_in.readline())
    # get each symbol
    for i in range(count): result += get_a_byte(parse_line(f.readline()))

    return result

  def process_message(msg):
    """
    Pick up keys from the message.

      Args:
        msg (str): decoded message from the file.

      Returns:
        tuple: tuple of strings. Public and private keys.
    """

    # length of the public key
    len_public_key = int(msg[_BLOCK_LENGTH_-_MAX_LENGTH_:_BLOCK_LENGTH_][::-1])
    # cut useless part of the message
    msg = msg[_BLOCK_LENGTH_:]
    # length of the private key
    len_private_key = int(msg[-_MAX_LENGTH_:])
    # cut useless part of the message
    msg = msg[:-_BLOCK_LENGTH_]

    return (msg[0:2*len_public_key:2], msg[1:2*len_private_key:2])

  if os.path.exists(_PATH_TO_THE_FILE_):

    file_in = open(_PATH_TO_THE_FILE_, "rb")
    cipher = AES.new(get_pass(), AES.MODE_CFB, parse_block(file_in))
    print('Keys were read')
    return process_message(cipher.decrypt(parse_block(file_in)).decode())
  else:

    print('There are no keys stored')
    return None

