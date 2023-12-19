# -*- coding: utf-8 -*-
"""
@author: Keith.Tucker

Python command-line script for retrieving files from cloud storage.

This program connects to an S3 bucket, finds the most reccent file
matching a file naming pattern, and downloads the file if the version in
cloud storage is newer than a local copy, or no local copy exists.

Parameters for the session and service connection can be obtained from
the environment variables listed below.

     AWS_ACCESS_KEY_ID
     AWS_SECRET_ACCESS_KEY
     AWS_PROFILE
     AWS_DEFAULT_REGION

Alternatively, the parameters may be read in from configuration files
named [HOME]/.aws/credentials and [HOME]/.aws/config, where [HOME] is the
home directory for the account under which the program is run. See the URL
below for more information .

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
"""

import argparse
import datetime
import logging
import os
import pathlib
import re
import sys

import boto3

DEFAULT_REGION = 'us-east-1'
DEFAULT_PROFILE = 'esf_dmp_published'

def find_latest_apr_file(bucket, fileNamePattern):
    latest = None
    fileName = None
    try:
        for bucketObj in bucket.objects.all():
            if latest is None or bucketObj.last_modified > latest:
                if re.match(fileNamePattern,bucketObj.key):
                    fileName = bucketObj.key
                    latest = bucketObj.last_modified
    except Exception as e:
        logging.error(e)
    return fileName, latest

if __name__ == '__main__':

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.ERROR))
    
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''Retrieve the latest file from cloud storage matching a file naming pattern.
''',
    epilog='''The program uses defaults for cloud storage access, which can be overridden with the following environment variables:
  AWS_ACCESS_KEY_ID: The identifier for authenticating access to cloud storage
  AWS_SECRET_ACCESS_KEY: The associated access key for authenticating access to cloud storage
  AWS_PROFILE: The name of the cloud storage location
  AWS_DEFAULT_REGION: The name of the associated Cloud Service Provider region in which the cloud storage is located
''')
    ap.add_argument('pattern', help='File naming pattern to use in searching cloud storage.') 
    ap.add_argument('-o','--output',help='Store files found in the specified directory.')
    ap.add_argument('-b','--bucket',action='append',dest='bucket', required=True,
        choices=['prod-esf-dmp-published', 'esftp-dmp-prod-curated','esftp-dmp-prod-analyzed'],
        help=f'The names of the cloud storage locations to search.')
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
        s3 = session.resource('s3')

        if args.output:
            outdir = pathlib.Path(args.output).resolve(strict=False)
            if outdir.exists():
                if outdir.is_dir:
                    os.chdir(outdir)
                else:
                    logging.error(f'{args.output} exists, but is not a directory. --output parameter must be a directory name.')
                    exit()
            else:
                outdir.mkdir(parents = True, exist_ok = True)
                os.chdir(outdir)

        file_not_found = True
        for bucket_name in args.bucket:
            bucket = s3.Bucket(bucket_name)

            file_name, mtime = find_latest_apr_file(bucket, args.pattern)

            if file_name is not None:
                file_not_found = False

                # If the file does not already exist or is older than the copy found in
                # cloud storage, download it for local use.
                download = False
                try:
                    fstat = os.stat(file_name)
                    if datetime.datetime.fromtimestamp(fstat.st_mtime,
                                                        tz=datetime.timezone.utc) < latest:
                        download = True
                except os.error:
                    # The file must not exist, so download it.
                    download = True
                if download:
                    # Download the object as a local file.
                    with open(file_name, 'wb') as f:
                        bucket.download_fileobj(file_name, f)
                print(f'Latest version file is {file_name} from bucket {bucket_name}.')

        if file_not_found:
            print(f'No file found in cloud storage matching naming pattern {args.pattern}')


    except Exception as e:
        logging.error('Error accessing cloud storage.', exc_info=e)
