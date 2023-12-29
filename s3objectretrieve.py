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

def find_latest_apr_files(bucket, file_name_patterns):
    file_list = []
    try:
        # Gather all the object names and last modified dates from the bucket,
        # for faster repeated iterations,
        cloud_file_list = []
        for bucket_obj in bucket.objects.all():
            cloud_file_list.append((bucket_obj.key,bucket_obj.last_modified))
        for pattern in file_name_patterns:
            latest = None
            file_name = None
            for bucket_file, bucket_latest in cloud_file_list:
                if latest is None or bucket_latest > latest:
                    if re.match(pattern,bucket_file):
                        file_name = bucket_file
                        latest = bucket_latest
            if file_name is not None:
                file_list.append((file_name,latest))
    except Exception as e:
        logging.error('Error searching for latest files in cloud storage.', exc_info=e)
    return file_list

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
    ap.add_argument('pattern', nargs='+', help='File naming pattern to use in searching cloud storage.') 
    ap.add_argument('-o', '--output', help='Store files found in the specified directory.')
    ap.add_argument('-b', '--bucket', action='append', dest='bucket', default=['prod-esf-dmp-published'],
        choices=['prod-esf-dmp-published', 'esftp-dmp-prod-curated','esftp-dmp-prod-analyzed'],
        help='The names of the cloud storage locations to search.')
    ap.add_argument('-p', '--profile', dest='profile', default=os.getenv('AWS_PROFILE', DEFAULT_PROFILE),
        help='Profile name to use for cloud storage access.')
    ap.add_argument('-r', '--region', dest='region', default=os.getenv('AWS_DEFAULT_REGION', DEFAULT_REGION),
        help='Region name to use for cloud storage access.')
    ap.add_argument('-k', '--key', help='Access key for cloud storage access.', dest='key',
        default=os.getenv('AWS_ACCESS_KEY_ID'))
    ap.add_argument('-s', '--secret', dest='secret', help='Secret access key for cloud storage access.',
        default=os.getenv('AWS_SECRET_ACCESS_KEY'))
    ap.add_argument('-n', '--noverify', action='store_false', help='Turn off SSL certificate validation.')
    args = ap.parse_args()

    try:
        session = boto3.Session(aws_access_key_id=args.key,
                                aws_secret_access_key=args.secret,
                                profile_name=args.profile,
                                region_name=args.region)
        s3 = session.resource('s3', verify=args.noverify)

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

            file_name_list = find_latest_apr_files(bucket, args.pattern)

            for file_name, latest in file_name_list:
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
                    print(f'File named {file_name} downloaded from bucket {bucket_name}.')
                else:
                    print(f'File named {file_name} was already the latest.')

        if file_not_found:
            print('No files found in cloud storage matching provided naming patterns.')


    except Exception as e:
        logging.error('Error accessing cloud storage.', exc_info=e)
