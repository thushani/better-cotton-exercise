import sqlite3
import os

# Store the database in the data directory
DATA_DIR = os.getenv("DATA_DIR", "/app/data" if os.path.exists("/app/data") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"))
DB_PATH = os.path.join(DATA_DIR, "chain_of_custody.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Organisations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS organisations (
        org_id TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        country TEXT,
        licence_status TEXT,
        licence_valid_to TEXT,
        licensed_volume_kg INTEGER
    )
    ''')
    
    # Create Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        txn_ref TEXT PRIMARY KEY,
        declared_on TEXT,
        seller_org_id TEXT,
        buyer_org_id TEXT,
        product TEXT,
        quantity REAL,
        unit TEXT,
        status TEXT,
        FOREIGN KEY (seller_org_id) REFERENCES organisations(org_id),
        FOREIGN KEY (buyer_org_id) REFERENCES organisations(org_id)
    )
    ''')
    
    conn.commit()
    conn.close()
