#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python program for generating APRs for ESF grants.

Python command-line program for generating an Annual Performance Report
(APR) for the Education Stabilization Fund (ESF) grants. The program
takes aggregated data captured in an online collection system and
generates an official record of a grantee's response for a given
reporting period.

This program connects to an S3 bucket, finds the most reccent files
containing ESF APR data (or uses the file named on the command line)
and generates Hypertext Markup Language (HTML) and Portable Document 
Format (PDF) files for each record in the file.

Parameters for the session and service connection for the S3 bucket can
be obtained from the environment variables listed below.

     AWS_ACCESS_KEY_ID
     AWS_SECRET_ACCESS_KEY
     AWS_PROFILE
     AWS_DEFAULT_REGION

Alternatively, the parameters may be read in from configuration files
named [HOME]/.aws/credentials and [HOME}/.aws/config, where [HOME} is the
home directory for the account under which the program is run. See the URL
below for more information.

https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

Additional command line arguments can be optionally specified to 
identify specific grantees for which an APR should be generated
(producing just that grantee's APR), to specify generating reports for
specific sub-funds (EANS, ESSER, GEER, or HEER), to specify a directory
for storing downloaded data files, to specify a directory for storing 
APR output files, and to specify which year of the ESF funds
availability for which to generate APRs.

Use the --help command line argument to get a full list of arguments.

@author: Keith.Tucker
"""

import argparse
import datetime
import logging
import os
import pathlib
import re
import sys
from typing import List, Iterator

import boto3
import openpyxl
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from esf_workbook_actions import APRWorkbookList, ESF_APR


_default_region = "us-east-1"
_default_profile = "esf_dmp_published"
_default_years = ["2020","2021"]
_default_subfunds = ["EANS","ESF-Gov","ESF-SEA","ESSER","GEER","HEER"]

_EANS_file_name_patterns = {"2021": "eans-2021-.*(raw|cleaned)", "2022": "eans-2022-.*(raw|cleaned)"}
_ESF_Gov_file_name_patterns = {"2020": "geer-2020-.*(raw|cleaned)", "2021": "geer-2021-.*(raw|cleaned)", "2022": "geer-2022-.*(raw|cleaned)"}
_ESF_SEA_file_name_patterns = {"2020": "esser-2020-.*(raw|cleaned)", "2021": "esfsea-2021-.*(raw|cleaned)", "2022": "esfsea-2022-.*(raw|cleaned)"}
_ESSER_file_name_patterns = {"2020": "esser-2020-.*(raw|cleaned)", "2021": "esser-2021-.*(raw|cleaned)", "2022": "esser-2022-.*(raw|cleaned)"}
_GEER_file_name_patterns = {"2020":"geer-2020-.*(raw|cleaned)", "2021":"geer-2021-.*(raw|cleaned)", "2022":"geer-2022-.*(raw|cleaned)"}
_HEER_file_name_patterns = {"2020": "heer-2020-.*(raw|cleaned)", "2021": "heer-2021-.*(raw|cleaned)", "2022": "heer-2022-.*(raw|cleaned)"}

_EANS_template_names = {"2021": "eans_apr.html","2022": "eans_apr.html"}
_ESF_Gov_template_names = {"2020": "geer_year1_apr.html", "2021": "geer_year2_apr.html", "2022": "geer_year3_apr.html"}
_ESF_SEA_template_names = {"2020": "esser_year1_apr.html", "2021": "esf_sea_year2_apr.html", "2022": "esf_sea_year3_apr.html"}
_ESSER_template_names = {"2020":"esser_year1_apr.html", "2021": "esser_year2_apr.html", "2022": "esser_year3_apr.html"}
_GEER_template_names = {"2020": "geer_year1_apr.html", "2021": "geer_year2_apr.html", "2022": "geer_year3_apr.html"}
_HEER_template_names = {"2020": "heer_year1_apr.html", "2021": "heer_year2_apr.html", "2022": "heer_year3_apr.html"}

def get_latest_apr_files(bucket, subfunds, years, data_dir):
    """Retrieve the latest data files from S3."""
    pattern_list = []
    pattern = None
    file_list = {}
    # Set the starting date for comparisons to the date the CARES Act was enacted.
    # All data files must have a date/time greater than that date.
    base_datetime = datetime.datetime(2020,3,20,tzinfo=datetime.UTC)
    for bucket_obj in bucket.objects.all():
        for subfund in subfunds:
            match subfund:
                case "EANS":
                    pattern_list = _EANS_file_name_patterns
                case "ESF-Gov":
                    pattern_list = _ESF_Gov_file_name_patterns
                case "ESF-SEA":
                    pattern_list = _ESF_SEA_file_name_patterns
                case "ESSER":
                    pattern_list = _ESSER_file_name_patterns
                case "GEER":
                    pattern_list = _GEER_file_name_patterns
                case "HEER":
                    pattern_list = _HEER_file_name_patterns
                case _:
                    continue

            for year in years:
                pattern = pattern_list.get(year,None)
            
                if pattern is None:
                    continue

                try:
                    matcher = re.compile(pattern)
                    latest = base_datetime
                    file_name = None
                    if matcher.match(bucket_obj.key):
                        # Parse the last_modified attribute, ignoring all but the date fields.
                        bucket_datetime = bucket_obj.last_modified
                        # Prefer files that have "reopen" in the name. So, if two files
                        # in cloud storage match the file naming pattern and were stored the
                        # same day, keep the one that has "reopen" in the name.
                        if bucket_datetime == latest and "reopen" in bucket_obj.key:
                            file_name = bucket_obj.key
                            latest = bucket_datetime
                        elif bucket_datetime > latest:
                            file_name = bucket_obj.key
                            latest = bucket_datetime
                    if file_name:
                        # A file was found in cloud storage matching the naming pattern.
                        # Now determine whether a local copy of that file is needed.
                        if data_dir:
                            file_path = data_dir / file_name
                        else:
                            file_path = pathlib.Path(file_name)

                        # Download the file if it does not already exist or is older than
                        # the file with the same name in the cloud storage.
                        download = False
                        if file_path.exists():
                            fstat = file_path.stat()
                            if datetime.datetime.fromtimestamp(fstat.st_mtime, tz=datetime.timezone.utc) < latest:
                                download = True
                        else:
                            download = True
                        if download:
                            # Download the object as a local file.
                            with file_path.open(mode='wb') as f:
                                bucket.download_fileobj(file_name, f)

                        # Use a tuple of the subfund and year for storing data file paths in a dictionary.
                        file_list[(subfund,year)] = file_path

                except Exception as e:
                    logging.info('Non-fatal exception in get_latest_apr_files.', exc_info=e)
    
    return file_list

def generate_apr(temp : Template, apr : ESF_APR) -> Iterator[str]:
    try:
        return temp.generate(apr = apr)
    except Exception as e:
        logging.error(f'Exception encountered generating APR for {apr.output_file_base_name}', exc_info=e)
        return None

def store_html(apr_html: Iterator[str], filename: pathlib.Path) -> None:
    try:
        with filename.open(mode="wt", encoding="utf-8") as hfp:
            for html_line in apr_html:
                hfp.write(html_line)
    except Exception as e:
        logging.error(f'Exception encountered storing HTML file {filename}.', exc_info=e)
        return

def yes_no(value):
    if value is not None:
        if value:
            return 'Yes'
    return 'No'

def check(value):
    if value is not None:
        if value:
            return 'checked'
    return ''

def dollars(value):
    if value is not None:
        if type(value) != float:
            value = float(value)
        return f'${value:,.2f}'
    return ''

def percent(value):
    if value is not None:
        if type(value) != float:
            value = float(value)
        return f'{value:.4f}'
    return ''

if __name__ == '__main__':

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.ERROR))
    
    # Retrieve the parameters from environment variables, if set.
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    profile = os.getenv('AWS_PROFILE', _default_profile)
    region = os.getenv('AWS_DEFAULT_REGION', _default_region)

    try:
        session = boto3.Session(aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key,
                                profile_name=profile,
                                region_name=region)
        s3 = session.resource('s3')
        bucket = s3.Bucket('prod-esf-dmp-published')

        ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Generate Annual Performance Reports for the ESF grants.

  Unless overridden on the command line, APRs for all grantees and all 
  sub-funds are generated in the current directory, for the first 3 
  years of the ESF funds availability (FY2020), and using data in the
  latest data files in cloud storage for those reporting years.
''',
        epilog='''The program uses defaults for cloud storage access, which can be overridden with the following environment variables:
  AWS_ACCESS_KEY_ID: The identifier for authenticating access to cloud storage
  AWS_SECRET_ACCESS_KEY: The associated access key for authenticating access to cloud storage
  AWS_PROFILE: The name of the cloud storage location
  AWS_DEFAULT_REGION: The name of the associated Cloud Service Provider region in which the cloud storage is located
''')
        ap.add_argument('-f','--filename', 
            help='Use the data in the specified file.') 
        ap.add_argument('-g','--grantee', action='append', 
            dest='grantees',
            help='Generate for just the specific grantee(s).')
        ap.add_argument('-y','--year',  action='append', dest='year', 
            choices=['2020','2021','2022'],
            help='Generate APRs for the specified reporting year(s).')
        ap.add_argument('-d','--data', 
            help='Copy data files from cloud storage to the specified directory.')
        ap.add_argument('-o','--output',
            help='Generate output files in the specified directory.')
        ap.add_argument('-s','--subfund',action='append', dest='subfund',
            choices=['EANS','ESF-Gov','ESF-SEA','ESSER','GEER','HEER'],
            help='Generate APRs for the specified sub-fund(s).')
        args = ap.parse_args()

        years = _default_years
        subfunds = _default_subfunds
        if args.year:
            years = args.year
        if args.subfund:
            subfunds = args.subfund

        datadir = None
        if args.data:
            datadir = pathlib.Path(args.data).resolve(strict=False)
            if datadir.exists():
                if not datadir.is_dir:
                    logging.error(f'{args.data} exists, but is not a directory. --data parameter must be a directory name.')
                    exit()
            else:
                datadir.mkdir(parents = True, exist_ok = True)

        file_list = {}
        if args.filename:
            file_list = [pathlib.Path(args.filename).resolve(strict=False).name]
        else:
            file_list = get_latest_apr_files(bucket, subfunds, years, datadir)
        if not file_list:
            logging.error('No APR data files found.')
            exit()

        outdir = None
        if args.output:
            outdir = pathlib.Path(args.output).resolve(strict=False)
            if outdir.exists():
                if not outdir.is_dir:
                    logging.error(f'{args.output} exists, but is not a directory. --output parameter must be a directory name.')
                    exit()
            else:
                outdir.mkdir(parents = True, exist_ok = True)

        # Create jinja2 environment, loading templates from a "templates" directory.
        # Excplicitly turn off autoescaping to avoid interfering with inserting HTML character code references.
        templatedir = pathlib.Path("templates").resolve(strict=False)
        env = Environment(loader=FileSystemLoader(templatedir.name),autoescape=select_autoescape(enabled_extensions=(),default_for_string=False))

        # Add custom filters for translating boolean values into "Yes" or "No" strings or checkboxes,
        # and for formatting dollar values and percentages
        env.filters["yes_no"] = yes_no
        env.filters["check"] = check
        env.filters["dollars"] = dollars
        env.filters["percent"] = percent

        for subfund in subfunds:
            template_list = []
            match subfund:
                case "EANS":
                    template_list = _EANS_template_names
                case "ESF-Gov":
                    template_list = _ESF_Gov_template_names
                case "ESF-SEA":
                    template_list = _ESF_SEA_template_names
                case "ESSER":
                    template_list = _ESSER_template_names
                case "GEER":
                    template_list = _GEER_template_names
                case "HEER":
                    template_list = _HEER_template_names
                case _:
                    logging.error(f'Invalid ESF subfund {subfund}')
                    continue

            for year in years:
                template_name = template_list.get(year,None)

                if not template_name:
                    logging.error(f'No template for subfund {subfund} year {year}.')
                    continue
                
                temp = env.get_template(name=template_name)

                filename = file_list.get((subfund,year),None)
                if filename:
                    efp = openpyxl.load_workbook(filename=filename, read_only=True, data_only=True)
                    aprs = APRWorkbookList(wb=efp, subfund=subfund, reporting_year=year, keys=args.grantees)
                    for apr in aprs:
                        print(f'Generating HTML APR {apr.output_file_base_name}')
                        apr_html = generate_apr(temp=temp, apr=apr)
                        if apr_html is None:
                            continue
                        html_path = pathlib.Path(apr.output_file_base_name).with_suffix('.html')
                        if outdir:
                            # Prepend the output directory name to the base file name.
                            html_path = outdir / html_path

                        store_html(apr_html, html_path)

                else:
                    logging.error(f'No data file for subfund {subfund} year {year}.')

    except Exception as e:
        logging.error('Exception in main function', exc_info=e)
