# -*- coding: utf-8 -*-

import os
import click
import logging
import datetime
import boto3

from hotbackup.utility import save_config, load_config, write_encrypted, read_encrypted
from hotbackup.services import get_aws_client


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
@click.argument('filename')
@click.option('--password', type=str, help='Optional password used to decrypt the file.')
def restore(filename, password):
  """Restores a file from Amazon S3.

  filename: The name of the file to download and restore.

  """
  log.info('Initiating file restore.')

  config = load_config()
  client = get_aws_client(config)

  out_filename = filename
  if filename.endswith('.enc'):
    out_filename = filename[:-4]

  client.download_file(config['s3_default_bucket'], filename, filename)
  response = read_encrypted(password, filename, False)

  with open(out_filename, 'wb') as output:
    output.write(response)

  log.info('Restore completed.')



@cli.command()
@click.argument('filepath')
@click.option('--password', type=str, help='Optional password used for encrypting the file.')
def backup(filepath, password):
  """Backup a file to Amazon AWS S3.

  filepath: The full path to the file, including file name.

  """
  log.info('Initiating file backup.')

  config = load_config()
  client = get_aws_client(config)

  filename = os.path.basename(filepath)
  encrypted = False
  now = datetime.datetime.utcnow()
  stored_filename = '{0}.{1}'.format(filename, now.strftime('%Y%m%d-%H%M%S'))

  with open(filepath, 'rb') as input:
    ciphertext = input.read()

  if password:
    log.info('Encrypting file...')
    stored_filename = '{0}.enc'.format(stored_filename)
    filepath = write_encrypted(password, stored_filename, ciphertext)
    encrypted = True

  client.upload_file(filepath, config['s3_default_bucket'], stored_filename)
  log.info('File backup completed.')


@cli.command()
def list():
  """List all files in the default S3 Bucket."""
  log.info('Listing files.')

  config = load_config()
  client = get_aws_client(config)

  response = client.list_objects(Bucket=config['s3_default_bucket'])
  log.debug(response)

  log.info('{0: <30}\t{1: <25}\t{2}'.format('Name', 'Last Modified', 'Size (bytes)'))
  for f in response.get('Contents', dict()):
    if not f['Key'].startswith('logs/'):
      log.info('{0: <30}\t{1!s: <25s}\t{2}'.format(f['Key'], f['LastModified'], f['Size']))


@cli.command()
def configure():
  """Amazon AWS Configuration."""
  log.info('Configuring application.')
  try:
    config = {}
    config['aws_access_key'] = click.prompt('AWS Access Key', type=str)
    config['aws_secret_key'] = click.prompt('AWS Secret Key', type=str)
    config['aws_region_name'] = click.prompt('AWS Region Name', type=str)
    config['s3_default_bucket'] = click.prompt('S3 Default Bucket Name', type=str)

    save_config(config)
  except KeyboardInterrupt:
    log.error('\nOperation cancelled by user.')

  log.info('Configuration file saved.')

