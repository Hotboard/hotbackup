# -*- coding: utf-8 -*-

import click
import logging

from hotbackup.utility import save_config


__version__ = '0.0.1'


log = logging.getLogger('hotbackup')


@click.group()
@click.option('--debug/--no-debug', default=False, help='In debug mode all log messages are shown.')
def cli(debug):
  log_level = (logging.DEBUG if debug else logging.INFO)
  logging.basicConfig(level=log_level, format='%(message)s')
  if debug:
    log.debug('Debug mode is on.')
  else:
    #suppress boto3 logging when not in debug mode
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('nose').setLevel(logging.CRITICAL)


@cli.command()
def configure():
  """Amazon AWS Configuration."""
  try:
    config = {}
    config['aws_access_key'] = click.prompt('AWS Access Key', type=str)
    config['aws_secret_key'] = click.prompt('AWS Secret Key', type=str)
    config['aws_region_name'] = click.prompt('AWS Region Name', type=str)

    save_config(config)
  except KeyboardInterrupt:
    log.error('\nOperation cancelled by user.')