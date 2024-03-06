import sqlite3

def get_db_connection():
    db = '.db'
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    sql = """
    CREATE TABLE IF NOT EXISTS 
    """
    conn.execute(sql)
    conn.commit()
    conn.close()