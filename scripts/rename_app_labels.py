"""
One-time database update for the app folder rename (AUTHENTICATE -> authenticate,
PARLEYPRO -> polls, etc.). Run it once on each database BEFORE starting the site
on the renamed code:

    python3 scripts/rename_app_labels.py /path/to/db.sqlite3

It backs up the database next to the original, then in a single transaction:
  - renames the app labels Django stores in django_migrations and django_content_type
  - renames the PARLEYPRO_* tables to polls_* (the other apps only change case,
    which SQLite table names ignore)

Running it again on an already-updated database does nothing.
"""
import shutil
import sqlite3
import sys
from datetime import datetime

RENAMES = {
    'AUTHENTICATE': 'authenticate',
    'HOME': 'home',
    'MISC': 'misc',
    'NEWMEMBER': 'newmember',
    'PHILANTHROPY': 'philanthropy',
    'SOBERSHEET': 'sobersheet',
    'PARLEYPRO': 'polls',
}


def main(db_path):
    backup = f"{db_path}.before-rename-{datetime.now():%Y%m%d-%H%M%S}"
    shutil.copy2(db_path, backup)
    print(f"Backed up database to {backup}")

    conn = sqlite3.connect(db_path)
    try:
        with conn:  # one transaction: everything is applied or nothing is
            for old, new in RENAMES.items():
                migrations = conn.execute("UPDATE django_migrations SET app = ? WHERE app = ?", (new, old)).rowcount
                content_types = conn.execute("UPDATE django_content_type SET app_label = ? WHERE app_label = ?", (new, old)).rowcount
                if migrations or content_types:
                    print(f"{old} -> {new}: {migrations} migration rows, {content_types} content types")

            # Table names are case-insensitive in SQLite, so only PARLEYPRO -> polls needs real renames
            tables = [row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'PARLEYPRO\\_%' ESCAPE '\\'")]
            for table in tables:
                new_table = 'polls_' + table[len('PARLEYPRO_'):]
                conn.execute(f'ALTER TABLE "{table}" RENAME TO "{new_table}"')
                print(f"Renamed table {table} -> {new_table}")
    finally:
        conn.close()
    print("Done.")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
