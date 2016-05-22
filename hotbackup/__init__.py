# -*- coding: utf-8 -*-

import os
import click
import logging
import datetime
import boto3
import tarfile

from shutil import copyfile

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
def decrypt(filename, password):
  """Decrypts a previously downloaded backup file from Amazon S3.

  filename: The name of the file to download and restore.

  """
  log.info('Decrypting file...')

  out_filename = filename
  if filename.endswith('.enc'):
    out_filename = filename[:-4]
    encrypted = True

  if not encrypted:
    log.info('Backup does not appear to be encrypted.')
    return

  response = read_encrypted(password, filename, False)
  with open(out_filename, 'wb') as output:
    output.write(response)

  os.remove(filename) #remove the encrypted file we just downloaded

  log.info('Decryption completed.')



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

  log.info('Downloading file...')
  client.download_file(config['s3_default_bucket'], filename, filename)

  encrypted = False
  out_filename = filename
  if filename.endswith('.enc'):
    out_filename = filename[:-4]
    encrypted = True

  if encrypted:
    log.info('Decrypting file...')
    response = read_encrypted(password, filename, False)

    with open(out_filename, 'wb') as output:
      output.write(response)

    os.remove(filename) #remove the encrypted file we just downloaded

  log.info('Restore completed.')



@cli.command()
@click.argument('filepath')
@click.option('--compress/--no-compress', default=True, help='Optional if the file or dir be compressed. Selected by default.')
@click.option('--password', type=str, help='Optional password used for encrypting the file.')
def backup(filepath, compress, password):
  """Backup a file to Amazon AWS S3.

  filepath: The full path to the file, including file name.

  """
  log.info('Initiating backup.')

  if not compress and os.path.isdir(os.path.abspath(filepath)):
    log.info('Uncompressed directories cannot be backed up. Aborting!')
    return

  config = load_config()
  client = get_aws_client(config)

  encrypted = False
  name = os.path.basename(os.path.abspath(filepath))
  now = datetime.datetime.utcnow()

  filename_format = '{0}.{1}.tgz'
  if not compress:
    filename_format = '{0}.{1}'

  file_to_upload = filename_format.format(name, now.strftime('%Y%m%d%H%M%S'))

  if compress:
    log.info('Compressing...')
    with tarfile.open(file_to_upload, 'w:gz') as tar:
      tar.add(filepath, arcname=name)
  else:
    log.info('Copying and renaming file.')
    copyfile(filepath, file_to_upload)

  filepath = file_to_upload

  if password:
    log.info('Encrypting...')
    with open(filepath, 'rb') as input:
      ciphertext = input.read()

    encrypted_filename = '{0}.enc'.format(filepath)
    encrypted_file = write_encrypted(password, encrypted_filename, ciphertext)
    encrypted = True
    filepath = encrypted_file

  log.info('Uploading...')
  client.upload_file(filepath, config['s3_default_bucket'], filepath)

  os.remove(file_to_upload)
  os.remove(encrypted_filename)

  log.info('Backup completed for {0}'.format(filepath))


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

