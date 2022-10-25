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

import boto3
import logging
import os

def list_s3_objects(session,bucketName):
    try:
        s3 = session.resource('s3')
        bucket=s3.Bucket(bucketName)
        for bucketObj in bucket.objects.all():
            print(f'{bucketObj}')
    except Exception as e:
        logging.error(e)
    
if __name__ == '__main__':

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.INFO))
    
    # Retrieve the ID and Key from environment variables, if set.
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    profile = os.getenv('AWS_PROFILE','esf_dmp_published')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

    try:
        session = boto3.Session(aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key,
                                profile_name=profile,
                                region_name=region)
    except Exception as e:
        logging.error(e)

    list_s3_objects(session,'prod-esf-dmp-published')

