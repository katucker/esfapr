#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python program for generating APRs for ESF grants.

Python command-line program for generating an Annual Performance Report
(APR) for the Education Stabilization Fund (ESF) grants. The program
takes aggregated data captured in an online collection system and
generates an official record of a grantee's response for a given
reporting period.

Use the --help command line argument to get a full list of arguments.

@author: Keith.Tucker
"""

import argparse
import datetime
import logging
import glob
import json
import os
import pathlib
import sys
from typing import List, Iterator

from jsonschema import validate,SchemaError,ValidationError
import openpyxl
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape, UndefinedError, TemplateAssertionError

from esf_workbook_actions import APRWorkbookList, ESF_APR

_DEFAULT_SCHEMA = "aprMap.schema.json"

def get_latest_apr_file(datafile_pattern: str) -> pathlib.Path:
    # Set the starting date for comparisons to the date the CARES Act was enacted.
    # All data files must have a date/time greater than that date.
    base_datetime = datetime.datetime(2020,3,20,tzinfo=datetime.UTC)
    latest_file = None

    try:
        matcher = glob.iglob(datafile_pattern)
        latest = base_datetime
        for filename in matcher:
            logging.info(f"Checking {filename}")
            file_path = pathlib.Path(filename)
            fstat = file_path.stat()
            if datetime.datetime.fromtimestamp(fstat.st_mtime, tz=datetime.timezone.utc) > latest:
                latest_file = file_path
    except Exception as e:
        logging.info('Nonfatal error in get_latest_apr_file.',exc_info=e)

    return latest_file

def generate_apr(temp : Template, apr : ESF_APR) -> Iterator[str]:
    try:
        return temp.generate(apr = apr)
    except TemplateAssertionError as e:
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
    try:
        if value is not None:
            if value:
                return 'Yes'
        return 'No'
    except (AttributeError, UndefinedError) as e:
        logging.info('Missing or undefined attribute in yes_no filter.', exc_info=e)
        return 'No'

def check(value):
    try:
        if value is not None:
            if value:
                return 'checked'
        return ''
    except (AttributeError, UndefinedError) as e:
        logging.info('Missing or undefined attribute in check filter.',exc_info=e)
        return ''

def dollars(value):
    try:
        if value is not None:
            if type(value) != float:
                try:
                    value = float(value)
                except ValueError as e:
                    logging.error(f'Error coercing {value} to floating point for dollars filter.',exc_info=e)
                    return ''
            return f'${value:,.2f}'
        return ''
    except (AttributeError, UndefinedError) as e:
        logging.info('Missing or undefined attribute in dollars filter.')
        return ''


def percent(value):
    try:
        if value is not None:
            if type(value) != float:
                try:
                    value = float(value)
                except ValueError as e:
                    logging.error(f'Error coercing {value} to floating point for percent filter',exc_info=e)
                    return ''
            return f'{value:.4f}'
        return ''
    except (AttributeError, UndefinedError) as e:
        logging.info('Missing or undefined attribute in percent filter.',exc_info=e)
        return ''

if __name__ == '__main__':

    logging.basicConfig(level=os.environ.get("LOGLEVEL",logging.ERROR))
    
    ap = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Generate Annual Performance Reports for the ESF grants.

  A single command line argument is required, consisting of a JSON file name specifying the APRs to generate.''')
    ap.add_argument('config', help='Name of the configuration file specifying the APRs to generate.')
    ap.add_argument('-s','--schema', default=_DEFAULT_SCHEMA,
        help='The path to a schema to use for validating the configuration files.')
    ap.add_argument('-e','--encoding', default='utf-8',
        help="Use the specified encoding for the files.")
    args = ap.parse_args()

    # Read the JSON schema and configuration file.
    with open(args.schema,'r',encoding=args.encoding) as sfp, open(args.config,'r',encoding=args.encoding) as ifp:
        schema = json.load(sfp)
        config = json.load(ifp)

        try:
            validate(instance=config,schema=schema)
            # Use the validated JSON configuration.
            outdir = config.get('output_path',None)
            if outdir is not None:
                # Convert the output path string to a Path object.
                outdir = pathlib.Path(outdir).resolve(strict=False)
                if outdir.exists():
                    if not outdir.is_dir:
                        logging.error(f'{config.output_path} exists, but is not a directory. The output_path value in the configuration file must be a directory name.')
                        exit()
                else:
                    outdir.mkdir(parents = True, exist_ok = True)

            # Find the latest file matching the datafile pattern in the configuration.
            apr_file = get_latest_apr_file(config['datafile_pattern'])
            if apr_file is None:
                logging.error(f'No datafile found matching pattern {config["datafile_pattern"]}')
                exit()
            else:
                print(f'Using data file {apr_file}')

            # Create the jinja2 environment for generating HTML files from templates.
            # Excplicitly turn off autoescaping to avoid interfering with inserting HTML character code references.
            env = Environment(loader=FileSystemLoader(config['template_path']),autoescape=select_autoescape(enabled_extensions=(),default_for_string=False))

            # Add custom filters for translating boolean values into "Yes" or "No" strings or checkboxes,
            # and for formatting dollar values and percentages
            env.filters["yes_no"] = yes_no
            env.filters["check"] = check
            env.filters["dollars"] = dollars
            env.filters["percent"] = percent

            temp = env.get_template(name=config['template_name'])

            efp = openpyxl.load_workbook(filename=apr_file, read_only=True, data_only=True)
            aprs = APRWorkbookList(wb=efp, config=config)
            for apr in aprs:
                if apr is None:
                    continue
                print(f'Generating HTML APR {apr.output_file_base_name}')
                apr_html = generate_apr(temp=temp, apr=apr)
                if apr_html is None:
                    continue
                html_path = pathlib.Path(apr.output_file_base_name).with_suffix('.html')
                if outdir:
                    # Prepend the output directory name to the base file name.
                    html_path = outdir / html_path

                store_html(apr_html, html_path)

        except SchemaError as se:
            logging.error("Schema error.", exc_info=se)
        except ValidationError as ve:
            logging.error("Instance validation error.", exc_info=ve)