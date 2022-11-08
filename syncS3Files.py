import argparse
import boto3
import datetime
import logging
import os
import pathlib
import time

DEST_FOLDER = "K:\\PPSS\\17. ESF\\S3_Data"
DEFAULT_REGION = 'us-east-1'
DEFAULT_PROFILE = 'esf_dmp_published'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Synchronize the latest files from cloud storage, copying them to a local destination folder.
''',
        epilog='''The program uses defaults for cloud storage access, which can be overridden with the following environment variables:
  AWS_ACCESS_KEY_ID: The identifier for authenticating access to cloud storage
  AWS_SECRET_ACCESS_KEY: The associated access key for authenticating access to cloud storage
  AWS_PROFILE: The name of the cloud storage location
  AWS_DEFAULT_REGION: The name of the associated Cloud Service Provider region in which the cloud storage is located
''')
    ap.add_argument('-o','--output',help='Copy files to the specified directory.', default=DEST_FOLDER)
    args = ap.parse_args()

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.INFO))
    
    # Retrieve the parameters from environment variables, if set.
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    profile = os.getenv('AWS_PROFILE', DEFAULT_PROFILE)
    region = os.getenv('AWS_DEFAULT_REGION', DEFAULT_REGION)

    try:
        startTime = time.time()
        session = boto3.Session(profile_name='esf_dmp_published',
                                region_name='us-east-1')
        s3 = session.resource('s3')
        bucket = s3.Bucket('prod-esf-dmp-published')
        filesCopied = 0
        for bucketObject in bucket.objects.all():
            if bucketObject.key[-1] == '/':
                # This object is just a folder designator, so skip it.
                continue
            filepath = pathlib.Path(f'{args.output}/{bucketObject.key}').resolve(strict=False)
            logging.info(f'Checking timestamp on {filepath}')
            download = False
            try:
                fstat = os.stat(filepath)
                if datetime.datetime.fromtimestamp(fstat.st_mtime, tz=datetime.timezone.utc) < bucketObject.last_modified:
                    download = True
            except os.error:
                # The file must not exist, so download it.
                download = True
            if download:
                # Create a corresponding directory locally for the object, if needed.
                foldername = filepath.parent
                if not foldername.exists():
                    foldername.mkdir(parents = True, exist_ok = True)
                # Download the object as a local file.
                s3.Object(bucketObject.bucket_name, bucketObject.key).download_file(
                    str(filepath))
                filesCopied += 1

        logging.info(f'\nTook {(time.time() - startTime):.1f} seconds to copy {filesCopied} files')
    except Exception as e:
        logging.error(e)
