# Overview

The purpose of this repo is to create a collection of Yale Humanitarian Research Lab reports related to Sudan and to upload
them to https://sudandigitalarchive.com.

## Documentation

- The archive API is documented [here](https://api.sudandigitalarchive.com/sda-api/docs/)
- YHRL reports are [here](https://medicine.yale.edu/lab/khoshnood/publications/reports/)

## Quickstart

1. Install `uv` and python 3.13
2. Create a virtual environment `uv venv .venv -p python3.13
3. Pin to that python `uv python pin .venv/bin/python3.13`
4. Run `uv sync`

## To Dos

- Put first raw scrape into its own folder and document workflow
- Then build something that uses the MCP server to check if new reports have been published
