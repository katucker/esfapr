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

defaultRegion = 'us-east-1'
defaultProfile = 'esf_dmp_published'

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
    
    # Retrieve the parameters from environment variables, if set.
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    profile = os.getenv('AWS_PROFILE', defaultProfile)
    region = os.getenv('AWS_DEFAULT_REGION', defaultRegion)

    try:
        session = boto3.Session(aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key,
                                profile_name=profile,
                                region_name=region)
        s3 = session.resource('s3')
        bucket = s3.Bucket('prod-esf-dmp-published')

        ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Retrieve the latest file from cloud storage matching a file naming pattern.
''',
        epilog='''The program uses defaults for cloud storage access, which can be overridden with the following environment variables:
  AWS_ACCESS_KEY_ID: The identifier for authenticating access to cloud storage
  AWS_SECRET_ACCESS_KEY: The associated access key for authenticating access to cloud storage
  AWS_PROFILE: The name of the cloud storage location
  AWS_DEFAULT_REGION: The name of the associated Cloud Service Provider region in which the cloud storage is located
''')
        ap.add_argument('-o','--output',help='Generate in the specified directory.')
        ap.add_argument('pattern', help='File naming pattern to use in searching cloud storage.') 
        args = ap.parse_args()
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
        fileName, mtime = find_latest_apr_file(bucket, args.pattern)

        if fileName:
            # If the file does not already exist or is older than the copy found in
            # cloud storage, download it for local use.
            download = False
            try:
                fstat = os.stat(fileName)
                if datetime.datetime.fromtimestamp(fstat.st_mtime,
                                                    tz=datetime.timezone.utc) < latest:
                    download = True
            except os.error:
                # The file must not exist, so download it.
                download = True
            if download:
                # Download the object as a local file.
                with open(fileName, 'wb') as f:
                    bucket.download_fileobj(fileName, f)
            print(f'Latest version file is {fileName}.')
        else:
            print(f'No file found in cloud storage matching naming pattern {args.pattern}')


    except Exception as e:
        logging.error(e)
