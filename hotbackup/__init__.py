# -*- coding: utf-8 -*-

import os
import click
import logging
import datetime
import boto3

from hotbackup.utility import save_config, load_config, write_encrypted


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
@click.argument('filepath')
@click.option('--password', type=str, help='Optional password used for encrypting the file.')
def backup(filepath, password):
  """Backup a file to Amazon AWS S3.

  filepath: The full path to the file, including file name.

  """
  log.info('Initiating file backup.')
  filename = os.path.basename(filepath)
  config = load_config()
  client = boto3.client('s3', region_name=config['aws_region_name'],
                              aws_access_key_id=config['aws_access_key'],
                              aws_secret_access_key=config['aws_secret_key'])

  encrypted = False
  now = datetime.datetime.utcnow()
  stored_filename = '{0}.{1}'.format(filename, now.strftime('%Y%m%d%H%M%S'))

  if password:
    log.info('Encrypting file...')
    stored_filename = '{0}.enc'.format(stored_filename)
    filepath = write_encrypted(password, stored_filename, filepath)
    encrypted = True

  client.upload_file(filepath, 'swipster-backup', stored_filename)
  log.info('File backup completed.')


@cli.command()
def configure():
  """Amazon AWS Configuration."""
  log.info('Configuring application.')
  try:
    config = {}
    config['aws_access_key'] = click.prompt('AWS Access Key', type=str)
    config['aws_secret_key'] = click.prompt('AWS Secret Key', type=str)
    config['aws_region_name'] = click.prompt('AWS Region Name', type=str)

    save_config(config)
  except KeyboardInterrupt:
    log.error('\nOperation cancelled by user.')

  log.info('Configuring file saved.')

