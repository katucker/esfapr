# esfapr
Various programs for working with data files containing data for Education Stabilization Fund Annual Performance Reports

s3objectlist.py lists the names of all objects in a specified Simple Storage Service (S3) bucket.

s3objectretrieve.py searches the S3 buckets specified on the command line for objects with names matching the patterns specified on the command line. The program downloads the latest file matching each pattern.

generate_esf_apr.py generates HTML files consisting of content in the approved Information Collection Request forms, along with the data provided by a given grantee. The program uses JSON configuration files to describe the mapping of an Excel spreadsheet containing all the data received for a reporting period and specific ESF subfund (EANS, ESSER, GEER, etc.) and other parameters for generating the HTML output. See the accompanying aprMap.schema.json for the JSON schema the configuration file must follow.
