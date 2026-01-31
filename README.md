# Overview

The purpose of this repo is to create a collection of Yale Humanitarian Research Lab reports related to Sudan 
and to upload them to https://sudandigitalarchive.com.

You can see the code the intiail ingest in `initial_ingest`. It is pretty messy - an initial scrape of the page,
a jupyter notebook to explore and clean the data, followed by some scripts to talk to the API and do the upload.

The `yale-report-ingester` Gemini CLI skill is used to regularly check for and archive new reports.

## Quickstart

1. Install `uv` and python 3.13
2. Create a virtual environment `uv venv .venv -p python3.13
3. Pin to that python `uv python pin .venv/bin/python3.13`
4. Run `uv sync`
5. Follow the instructions at 
[https://github.com/Sudan-Digital-Archive/mcp-server](https://github.com/Sudan-Digital-Archive/mcp-server) to install
the MCP server running locally over `stdio`
6. Install the gemini skill `gemini skills install skills/yale-report-ingester --scope workspace`
7. Ask Gemini CLI to check for new reports:

> "Check for new Yale Humanitarian Research Lab reports and ingest them if found."

The skill will:

1.  Run the local scraper to find the latest report.
2.  Compare it against the `yale_manifest.json`.
3.  Verify with the Sudan Digital Archive API (handling schema errors automatically).
4.  Crawl and ingest the report if it's new.
5.  Update the local manifest.

## Documentation

- The archive API is documented [here](https://api.sudandigitalarchive.com/sda-api/docs/)
- YHRL reports are [here](https://medicine.yale.edu/lab/khoshnood/publications/reports/)

