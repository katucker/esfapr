# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 15:57:55 2022

@author: Keith.Tucker

Python command-line script for listing objects in an S3 bucket.

Parameters for the session and service connection can be obtained from
the environment variables listed below.

     AWS_ACCESS_KEY_ID
     AWS_SECRET_ACCESS_KEY
     AWS_PROFILE
     AWS_DEFAULT_REGION

Alternatively, the parameters may be read in from configuration files
named [HOME]/.aws/credentials and [HOME}/.aws/config, where [HOME} is the
home directory for the account under which the program is run. See the URL
below for more information .

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
"""

import argparse
import boto3
import logging
import os

DEFAULT_REGION = 'us-east-1'
DEFAULT_PROFILE = 'esf_dmp_published'

def list_s3_objects(session,bucketName):
    try:
        s3 = session.resource('s3')
        bucket=s3.Bucket(bucketName)
        for bucketObj in bucket.objects.all():
            print(f'{bucketObj.key} last modified {bucketObj.last_modified}')
    except Exception as e:
        logging.error('Error listing bucket contents.', exc_info=e)
    
if __name__ == '__main__':

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.ERROR))
    
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''List the files in cloud storage.
''',
        epilog='''The program uses defaults for cloud storage access, which can be overridden with the following environment variables:
  AWS_ACCESS_KEY_ID: The identifier for authenticating access to cloud storage
  AWS_SECRET_ACCESS_KEY: The associated access key for authenticating access to cloud storage
  AWS_PROFILE: The name of the cloud storage location
  AWS_DEFAULT_REGION: The name of the associated Cloud Service Provider region in which the cloud storage is located
''')
    ap.add_argument('-b','--bucket',action='append',dest='bucket', required=True,
        choices=['prod-esf-dmp-published', 'esftp-dmp-prod-curated','esftp-dmp-prod-analyzed'],
        help=f'The names of the cloud storage locations to likst.')
    ap.add_argument('-p','--profile',dest='profile',default=os.getenv('AWS_PROFILE', DEFAULT_PROFILE),
        help='Profile name to use for cloud storage access.')
    ap.add_argument('-r','--region',dest='region',default=os.getenv('AWS_DEFAULT_REGION', DEFAULT_REGION),
        help='Region name to use for cloud storage access.')
    ap.add_argument('-k','--key',help='Access key for cloud storage access.',dest='key',
        default=os.getenv('AWS_ACCESS_KEY_ID'))
    ap.add_argument('-s','--secret',dest='secret',help='Secret access key for cloud storage access.',
        default=os.getenv('AWS_SECRET_ACCESS_KEY'))
    args = ap.parse_args()

    try:
        session = boto3.Session(aws_access_key_id=args.key,
                                aws_secret_access_key=args.secret,
                                profile_name=args.profile,
                                region_name=args.region)
        for bucket in args.bucket:
            print(f'Contents of bucket {bucket}:')
            list_s3_objects(session,bucket)

    except Exception as e:
        logging.error('Error creating session.',exc_info=e)


