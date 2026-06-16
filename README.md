# EOIR Immigration Decisions Scraper

Collects and tracks federal immigration precedent decisions from the U.S. Department of Justice Executive Office for Immigration Review (EOIR), updated daily.

**Browse the data:** [datasette-lite](https://lite.datasette.io/?url=https://raw.githubusercontent.com/DagmarRoth/Immigration/main/eoir_decisions.db)

## Methodology

This scraper collects federal immigration precedent decisions from the U.S. Department of Justice Executive Office for Immigration Review (EOIR), specifically BIA/AG Precedent Decisions (Volumes 24–29) and OCAHO Published Decisions (Volumes 14–22). It targets only published, publicly accessible federal decisions — no state courts, no unpublished rulings. The timeframe begins with Volume 24 (BIA) and Volume 14 (OCAHO), capturing all decisions through the present, with daily updates to detect new additions.

The scraper is built in Python using `requests` and `BeautifulSoup4`. It follows a change-detection architecture: on each run it compares newly scraped records against the existing dataset by decision URL and caches metadata locally, requesting only pages where new decisions may have appeared. This limits requests to the EOIR site to the minimum necessary — typically a handful of index pages per run rather than a full re-crawl. No PDFs are downloaded in the default configuration.

Each decision record captures up to 27 fields including title, volume, decision date, case number, PDF URL, and extracted date components for time-series analysis. Missing fields are stored as `null` rather than dropped. Duplicate detection runs on URL as a primary key; if a record's metadata changes between runs (e.g., a corrected date), the update is logged in a dated changelog file. Errors are isolated per-decision and written to a separate error log so a single bad record does not abort the run.

Key analytical dimensions tracked over time: publication rate by volume, decision date distribution by month and year, coverage gaps, and the ratio of BIA to AG-certified decisions. The dataset is published as a queryable SQLite database via datasette-lite, updated daily through GitHub Actions.
