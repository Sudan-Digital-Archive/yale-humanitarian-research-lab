---
name: yale-report-ingester
description: Checks for and ingests new reports from the Yale Humanitarian Research Lab into the Sudan Digital Archive. 
  Use when the user asks to update Yale reports or check for new publications.
---

# Yale Report Ingester

This skill automates the process of checking for new Yale Humanitarian Research Lab (HRL) reports and ingesting 
them into the Sudan Digital Archive (SDA). It uses a local Python script to fetch the latest report and compares it 
against a local manifest to avoid unnecessary work.

## Prerequisites

- **Python Script:** `skills/yale-report-ingester/scripts/get_latest_yale_reports.py` must exist in the repository.
- **Manifest:** `.gemini/yale_manifest.json` must exist (tracks the last ingested URL).
- **Environment:** `uv` must be installed to run the Python script.
- **SDA Subject ID:** `37` (Yale Humanitarian Research Lab).

## Workflow

### 1. Check for Updates
1.  **Execute the scraper:** Run the following command to get the latest report metadata:
    ```bash
    uv run initial_ingest/get_latest_yale_reports.py
    ```
    *Output will be a JSON object with keys: `title`, `date` (ISO format), `url`.*

2.  **Read Manifest:** Read the content of `.gemini/yale_manifest.json`.

3.  **Compare:**
    - If `scraper_output.url` == `manifest.last_ingested_url`:
        - **STOP.** Inform the user: "No new reports found. The latest report '[Title]' is already in the archive."
    - If they differ, proceed to **Verification**.

### 2. Verification (Safety Check)
*Before adding anything, ensure it's not already in the archive.*

1.  **Search Archive:** Call `list_accessions` with `urlFilter` set to the `scraper_output.url`.
    - **CRITICAL - Error Handling:** If the tool returns a JSON Schema error (e.g., `no schema with key or ref...`), 
    **YOU MUST RETRY THE CALL IMMEDIATELY**. This is a known intermittent issue.

2.  **Analyze Result:**
    - **IF items found:** The report exists in the archive but the manifest is out of sync.
        - **Action:** Update `.gemini/yale_manifest.json` with the new URL and date.
        - **Stop.** Inform the user: "Report '[Title]' was already archived. Local manifest updated."
    - **IF items empty:** The report is truly new. Proceed to **Ingestion**.

### 3. Ingestion
1.  **Create Accession:** Call `create_accession_crawl` with the following parameters:
    - `url`: `scraper_output.url`
    - `metadata_title`: `scraper_output.title`
    - `metadata_time`: `scraper_output.date` (Ensure it is a valid string, e.g., "2026-01-16")
    - `metadata_subjects`: `[37]`
    - `metadata_language`: `"en"`
    - `metadata_format`: `"wacz"`
    - `is_private`: `false`

    - **Error Handling:** Again, **RETRY IMMEDIATELY** if you encounter the JSON Schema error.

2.  **Confirm Success:** Ensure the tool call was successful by polling for the URL using the list accessions MCP
    tool. Note this will take several minutes for the URL to get crawled and appear in the archive.

### 4. Update State
1.  **Update Manifest:** Write the new details to `.gemini/yale_manifest.json`:
    ```json
    {
      "last_ingested_url": "<NEW_URL>",
      "last_check_date": "<TODAY_DATE>"
    }
    ```

2.  **Finish:** Inform the user: "Successfully ingested new report: [Title]."