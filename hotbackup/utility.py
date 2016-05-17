# -*- coding: utf-8 -*-

import os
import logging
import yaml


__all__ = ['load_config', 'save_config']


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