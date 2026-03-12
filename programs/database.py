import sqlite3

DB  = 'cpes.db'
table_name = 'cpes'

def create_db() -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
   
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cpes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR NOT NULL, 
        reference_links TEXT,
        cpe_22_uri TEXT,
        cpe_23_uri TEXT UNIQUE,
        cpe_22_deprecation_date DATE,
        cpe_23_deprecation_date DATE)''')
    con.commit()
    con.close()


def insert_cpes_batch(cpe_batch: list) -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    cur.executemany('''
        INSERT OR IGNORE INTO cpes (title, reference_links, cpe_22_uri, cpe_23_uri, cpe_22_deprecation_date, cpe_23_deprecation_date)
        VALUES (?, ?, ?, ?, ?, ?)''', cpe_batch)
    con.commit()
    con.close()

def get_all_cpes() -> list:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('SELECT * FROM cpes')
    cpes = cur.fetchall()
    con.close()
    return cpes

def delete_cpe(cpe_id:int) -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('DELETE FROM cpes WHERE id = ?', (cpe_id,))
    con.commit()
    con.close()

def drop_table() -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {table_name}')
    con.commit()
    con.close()

def truncate_cpes() -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(f"DELETE FROM {table_name}")
    cur.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
    con.commit()
    con.close()

def get_total_cpes_count() -> int:
    
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('SELECT COUNT(*) FROM cpes')
    count = cur.fetchone()[0]
    con.close()
    return count

def get_cpes_paginated(page: int = 1, limit: int = 10) -> list:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    offset = (page - 1) * limit
    cur.execute('''
        SELECT id, title, reference_links, cpe_22_uri, cpe_23_uri, cpe_22_deprecation_date, cpe_23_deprecation_date
        FROM cpes
        ORDER BY id
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    cpes = cur.fetchall()
    con.close()
    return cpes

def search_cpes(cpe_title: str = None, cpe_22_uri: str = None, cpe_23_uri: str = None, deprecation_date: str = None) -> list:
    
    con = sqlite3.connect(DB)
    cur = con.cursor()
    
    # Build dynamic WHERE clause
    where_clauses = []
    params = []
    
    if cpe_title:
        where_clauses.append('title LIKE ?')
        params.append(f'%{cpe_title}%')
    
    if cpe_22_uri:
        where_clauses.append('cpe_22_uri LIKE ?')
        params.append(f'%{cpe_22_uri}%')
    
    if cpe_23_uri:
        where_clauses.append('cpe_23_uri LIKE ?')
        params.append(f'%{cpe_23_uri}%')
    
    if deprecation_date:
        # CPEs deprecated before the given date (either CPE 2.2 or 2.3)
        where_clauses.append('(cpe_22_deprecation_date < ? OR cpe_23_deprecation_date < ?)')
        params.extend([deprecation_date, deprecation_date])
    
    # Build the query
    query = '''
        SELECT id, title, reference_links, cpe_22_uri, cpe_23_uri, cpe_22_deprecation_date, cpe_23_deprecation_date
        FROM cpes
    '''
    
    if where_clauses:
        query += ' WHERE ' + ' AND '.join(where_clauses)
    
    query += ' ORDER BY id'
    
    cur.execute(query, params)
    cpes = cur.fetchall()
    con.close()
    return cpes

if __name__ == "__main__":
    drop_table()
    create_db()
    print("Database initialized successfully!")
