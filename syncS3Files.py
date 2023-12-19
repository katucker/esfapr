import argparse
import boto3
import datetime
import logging
import os
import pathlib
import time
import zipfile

DEST_FOLDER = "S3_Data"
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
    ap.add_argument('-o','--output',help='Copy files to the specified directory.', dest='output', default=DEST_FOLDER)
    ap.add_argument('-u','--unzip', help='Force unzip of all archive files.', action='store_true', dest='unzip')
    ap.add_argument('-b','--bucket',action='append',dest='bucket', required=True,
        choices=['prod-esf-dmp-published', 'esftp-dmp-prod-curated','esftp-dmp-prod-analyzed'],
        help=f'The names of the cloud storage locations to synchronize.')
    ap.add_argument('-p','--profile',dest='profile',default=os.getenv('AWS_PROFILE', DEFAULT_PROFILE),
        help='Profile name to use for cloud storage access.')
    ap.add_argument('-r','--region',dest='region',default=os.getenv('AWS_DEFAULT_REGION', DEFAULT_REGION),
        help='Region name to use for cloud storage access.')
    ap.add_argument('-k','--key',help='Access key for cloud storage access.',dest='key',
        default=os.getenv('AWS_ACCESS_KEY_ID'))
    ap.add_argument('-s','--secret',dest='secret',help='Secret access key for cloud storage access.',
        default=os.getenv('AWS_SECRET_ACCESS_KEY'))
    args = ap.parse_args()

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.ERROR))

    try:    
        session = boto3.Session(profile_name=args.profile,
                                region_name=args.region,
                                aws_access_key_id=args.key,
                                aws_secret_access_key=args.secret)
        s3 = session.resource('s3')
    except Exception as e:
        logging.error('Error creating cloud session.',exc_info=e)
        exit()

    for bucket in args.bucket:
        try:
            logging.info(f'Synchronizing {bucket}')
            startTime = time.time()
            bucket = s3.Bucket(bucket)
            filesCopied = 0
            for bucketObject in bucket.objects.all():
                if bucketObject.key[-1] == '/':
                    # This object is just a folder designator, so skip it.
                    continue
                filepath = pathlib.Path(f'{args.output}/{bucketObject.key}').resolve(strict=False)
                foldername = filepath.parent
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
                    if not foldername.exists():
                        foldername.mkdir(parents = True, exist_ok = True)
                    # Download the object as a local file.
                    s3.Object(bucketObject.bucket_name, bucketObject.key).download_file(str(filepath))
                    filesCopied += 1
                    logging.info(f'Copied file {filepath}')
                if download or args.unzip:
                    # Extract files from ZIP archives
                    if filepath.suffix.lower() == ".zip":
                        logging.info('Extracting ZIP archive contents.')
                        try:
                            with zipfile.ZipFile(filepath, 'r') as zf:
                                zf.extractall(path=foldername)
                        except Exception as e:
                            logging.error(e)

            logging.info(f'\nTook {(time.time() - startTime):.1f} seconds to copy {filesCopied} files')
        except Exception as e:
            logging.error('Error synchronizing bucket.', exc_info=e)
