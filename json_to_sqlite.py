"""
Convert EOIR JSON data files to a single SQLite database for Datasette.

Run this after the scraper:
    python3 json_to_sqlite.py

Output: eoir_decisions.db  (used by: datasette publish vercel eoir_decisions.db)
"""

import json
import os
import sqlite_utils

DB_PATH = "eoir_decisions.db"

db = sqlite_utils.Database(DB_PATH)


def load_table(table_name, json_path, pk="url", indexes=None):
    if not os.path.exists(json_path):
        print(f"  ⚠️  {json_path} not found — skipping {table_name}")
        return
    with open(json_path) as f:
        rows = json.load(f)
    if not rows:
        print(f"  ⚠️  {json_path} is empty")
        return
    db[table_name].insert_all(rows, pk=pk, replace=True, alter=True)
    for col_list in (indexes or []):
        db[table_name].create_index(col_list, if_not_exists=True)
    print(f"  ✓ {table_name}: {len(rows):,} rows")


print("Building eoir_decisions.db ...")

load_table(
    "bia_ag_decisions",
    "data/bia_ag_decisions.json",
    indexes=[
        ["citation_year"],
        ["citation_volume"],
        ["deciding_body"],
        ["is_attorney_general"],
        ["source_volume_number"],
        ["decision_id"],
        ["scraped_date"],
    ],
)

load_table(
    "ocaho_decisions",
    "data/ocaho_decisions.json",
    indexes=[
        ["case_type_code"],
        ["year_from_case_number"],
        ["source_volume_number"],
        ["is_sub_decision"],
        ["is_caho_decision"],
        ["reference_base"],
        ["scraped_date"],
    ],
)

# Enable full-text search on the text-heavy columns
for table, cols in [
    ("bia_ag_decisions",  ["case_name", "headnote", "full_text"]),
    ("ocaho_decisions",   ["case_name", "full_text"]),
]:
    if table in db.table_names():
        try:
            db[table].enable_fts(cols, create_triggers=True)
            print(f"  ✓ FTS enabled on {table}({', '.join(cols)})")
        except Exception:
            pass  # FTS already exists; triggers from prior run are fine

size_mb = os.path.getsize(DB_PATH) / 1024 / 1024
print(f"\nDone — {DB_PATH} ({size_mb:.1f} MB)")
