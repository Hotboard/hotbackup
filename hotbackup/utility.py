# -*- coding: utf-8 -*-

import os
import logging
import yaml

from simplecrypt import encrypt, decrypt


__all__ = ['load_config', 'save_config', 'read_encrypted', 'write_encrypted']


log = logging.getLogger(__name__)


CONFIG_FILE = os.path.expanduser('~/.hotbackup-config.yml')


def load_config():
  """Loads the default AWS configuration.

  Returns:
    dict: The configuration object.

  """
  log.debug('Loading configuration file.')
  return yaml.load(open(CONFIG_FILE))


def save_config(config):
  """Saves the AWS configuration.

  Args:
    config (dict): Config object to save.

  """
  yaml.dump(config, open(CONFIG_FILE, 'w'), default_flow_style=False)
  log.debug('Config written in {0}'.format(CONFIG_FILE))


def read_encrypted(password, filename, string=True):
  """Decrypts a file

  Args:
    password (str): The password for the decryption.
    filename (str): The output name of the clear text file.
    string (bool): UTF-8 data or no, used for decoding.

  Returns:
    str: The descrypted data.

  """
  log.debug('Decrypting file.')
  with open(filename, 'rb') as input:
    ciphertext = input.read()
    plaintext = decrypt(password, ciphertext)
    if string:
      return plaintext.decode('utf8')
    else:
      return plaintext


def write_encrypted(password, filename, data):
  """Encrypts a file

  Args:
    password (str): The password for the encryption.
    filename (str): The output name of the encrypted file.
    data (str): The path to the data to be encrypted.

  Returns:
    str: The name and path of the encrypted file.

  """
  with open(filename, 'wb') as output:
    ciphertext = encrypt(password, data)
    output.write(ciphertext)
    log.debug('Encrypted file {0}'.format(output.name))
    return output.name

