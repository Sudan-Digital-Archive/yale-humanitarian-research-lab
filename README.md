# Overview

The purpose of this repo is to create a collection of Yale Humanitarian Research Lab reports related to Sudan 
and to upload them to https://sudandigitalarchive.com.

You can see the code the intiail ingest in `initial_ingest`. It is pretty messy - an initial scrape of the page,
a jupyter notebook to explore and clean the data, followed by some scripts to talk to the API and do the upload.

The file `main.py` is meant to be regularly run to check for any new reports to archive. At the time of writing this
is intended to be manually run; it may evolve into a cron pattern in a digital ocean function or similar as the
archive evolves.

## Documentation

- The archive API is documented [here](https://api.sudandigitalarchive.com/sda-api/docs/)
- YHRL reports are [here](https://medicine.yale.edu/lab/khoshnood/publications/reports/)

## Quickstart

1. Install `uv` and python 3.13
2. Create a virtual environment `uv venv .venv -p python3.13
3. Pin to that python `uv python pin .venv/bin/python3.13`
4. Run `uv sync`

