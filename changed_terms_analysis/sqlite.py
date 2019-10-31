from contextlib import contextmanager
from pathlib import Path
import sqlite3
from .tools import net_change


@contextmanager
def sqlite_database(db_path):
    if db_path is None:
        yield None
        return

    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE pages (
            id TEXT NOT NULL PRIMARY KEY,
            first_version_id TEXT NOT NULL,
            last_version_id TEXT NOT NULL,
            url TEXT NOT NULL,
            view_url TEXT NOT NULL,
            title TEXT,
            status INTEGER,
            first_version_date TEXT NOT NULL,
            last_version_date TEXT NOT NULL,
            percent_changed INTEGER NOT NULL
        );

        CREATE UNIQUE INDEX pages_page_id ON pages (id);
        CREATE INDEX pages_percent_changed ON pages (percent_changed);
        CREATE INDEX pages_url ON pages (url COLLATE NOCASE);
        CREATE INDEX pages_title ON pages (title COLLATE NOCASE);

        CREATE TABLE term_changes (
            page_id TEXT NOT NULL,
            term TEXT NOT NULL,
            change_count INTEGER NOT NULL,
            FOREIGN KEY(page_id) REFERENCES pages(id)
        );

        CREATE UNIQUE INDEX term_changes_key ON term_changes (page_id, term);
        CREATE INDEX term_changes_term ON term_changes (term);
        CREATE INDEX term_changes_change_count ON term_changes (change_count);
    """)
    cursor.close()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def write_page_to_sqlite(page, db=None, key_terms=None):
    if not db:
        return

    net_terms = net_change(*page['terms'])
    db.execute("INSERT INTO pages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (page['id'],
                page['first_id'],
                page['last_id'],
                page['url'],
                f'https://monitoring.envirodatagov.org/page/{page["id"]}/{page["first_id"]}..{page["last_id"]}',
                page['title'],
                page['status'],
                page['first_date'],
                page['last_date'],
                page['percent_changed'],))

    db.executemany("INSERT INTO term_changes VALUES (?, ?, ?)",
                   ((page['id'], term, count)
                    for term, count in net_terms.items()
                    if (key_terms is None or term in key_terms)))
    db.commit()



