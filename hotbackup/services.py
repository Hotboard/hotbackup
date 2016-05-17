# -*- coding: utf-8 -*-

import boto3
import logging

from hotbackup.utility import load_config, read_encrypted, write_encrypted


__all__ = ['get_aws_client']


log = logging.getLogger(__name__)


def get_aws_client(config):
  """Returns an S3 service.

  Args:
    config (dict): The configuration object.

  Returns:
    obj: The correctly configured client service.

  """
  log.debug('Initializing S3 client.')
  client = boto3.client('s3', region_name=config['aws_region_name'],
                              aws_access_key_id=config['aws_access_key'],
                              aws_secret_access_key=config['aws_secret_key'])
  return client