# -*- coding: utf-8 -*-
import logging
import os
import oss2
import json
import time


# Copy multiple objects specified by keys from src_bucket to dest_bucket.

# event format
# {
#   "src_bucket": "",
#   "dest_bucket": "",
#   "key": "a"
# }

def handler(event, context):
  logger = logging.getLogger()
  evt = json.loads(event)
  logger.info("Handling event: %s", evt)
  src_endpoint = 'https://oss-%s-internal.aliyuncs.com' % context.region
  src_client = get_oss_client(context, src_endpoint, evt["src_bucket"])
  dest_client = get_oss_client(context, evt.get("dest_oss_endpoint") or os.environ['DEST_OSS_ENDPOINT'], evt["dest_bucket"])

  copy(src_client, dest_client, evt["key"])

  return {}


def copy(src_client, dest_client, key):
  logger = logging.getLogger()
  logger.info("Starting to copy %s", key)
  start_time = time.time()
  object_stream = src_client.get_object(key)
  res = dest_client.put_object(key, object_stream)
  end_time = time.time()
  logger.info('Copied %s in %s secs', key, end_time-start_time)

def get_oss_client(context, endpoint, bucket):
  creds = context.credentials
  if creds.security_token != None:
    auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token)
  else:
    # for local testing, use the public endpoint
    endpoint = str.replace(endpoint, "-internal", "")
    auth = oss2.Auth(creds.access_key_id, creds.access_key_secret)
  return oss2.Bucket(auth, endpoint, bucket)