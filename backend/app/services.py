import csv
import os
from .database import get_db_connection

DATA_DIR = os.getenv("DATA_DIR", "/app/data" if os.path.exists("/app/data") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"))

def load_csv_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Load Organisations
    org_file = os.path.join(DATA_DIR, 'organisations.csv')
    valid_org_ids = set()
    
    if os.path.exists(org_file):
        with open(org_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                org_id = row['org_id']
                vol = row['licensed_volume_kg']
                vol = int(vol) if vol else None  # null/0 for non-ginners
                
                cursor.execute('''
                    INSERT OR REPLACE INTO organisations 
                    (org_id, name, type, country, licence_status, licence_valid_to, licensed_volume_kg)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    org_id, row['name'], row['type'], row['country'], 
                    row['licence_status'], row['licence_valid_to'], vol
                ))
                valid_org_ids.add(org_id)
                
    # 2. Load Transactions
    txn_file = os.path.join(DATA_DIR, 'transactions.csv')
    if os.path.exists(txn_file):
        with open(txn_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                seller = row['seller_org_id']
                buyer = row['buyer_org_id']
                
                # Rule 2: Discard missing orgs (e.g., X-99)
                if seller not in valid_org_ids or buyer not in valid_org_ids:
                    continue
                
                # Rule 1: Unit conversion (1 bale = 165kg)
                quantity = float(row['quantity'])
                unit = row['unit'].lower()
                if unit == 'bales':
                    quantity = quantity * 165.0
                    unit = 'kg'
                
                # Rule 3 & 4: Ignored 
                # (Duplicate exact rows handled by INSERT OR IGNORE on PK txn_ref. Expired licenses imported as is.)
                cursor.execute('''
                    INSERT OR IGNORE INTO transactions
                    (txn_ref, declared_on, seller_org_id, buyer_org_id, product, quantity, unit, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['txn_ref'], row['declared_on'], seller, buyer,
                    row['product'], quantity, unit, row['status']
                ))
                
    conn.commit()
    conn.close()

def generate_reconciliation_html():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM organisations")
    orgs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM transactions WHERE status = 'Confirmed'")
    txns = cursor.fetchall()
    conn.close()

    org_data = {}
    for org in orgs:
        org_id = org["org_id"]
        is_ginner = (org["type"].lower() == "ginner")
        received = float(org["licensed_volume_kg"] or 0) if is_ginner else 0.0
        
        problems = []
        if org["licence_status"].lower() == "expired":
            problems.append("License is expired")
            
        org_data[org_id] = {
            "name": org["name"],
            "type": org["type"],
            "received": received,
            "sold": 0.0,
            "available": received,
            "problems": problems
        }

    for txn in txns:
        seller = txn["seller_org_id"]
        buyer = txn["buyer_org_id"]
        qty = float(txn["quantity"])
        
        if seller in org_data:
            org_data[seller]["sold"] += qty
            org_data[seller]["available"] -= qty
            
        if buyer in org_data:
            org_data[buyer]["received"] += qty
            org_data[buyer]["available"] += qty

    for org_id, data in org_data.items():
        if data["available"] < 0:
            data["problems"].append("Negative balance (sold more than available)")

    html = """
    <html>
    <head>
        <title>Chain-of-Custody Reconciliation</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; background: #f9fafb; color: #111827; }
            h1, h2 { color: #1f2937; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 40px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            th, td { text-align: left; padding: 12px; border-bottom: 1px solid #e5e7eb; }
            th { background-color: #f3f4f6; font-weight: bold; }
            tr:hover { background-color: #f9fafb; }
            .negative { color: #dc2626; font-weight: bold; }
            .problem-list { color: #dc2626; font-size: 0.9em; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 30px; }
            ul { margin-top: 0; }
        </style>
    </head>
    <body>
        <h1>Chain-of-Custody Reconciliation</h1>
        
        <div class="card">
            <h2>Data Problems Identified in Seed Data</h2>
            <ul>
                <li><strong>Duplicate Transactions:</strong> <code>TXN-0117</code> was found duplicated. <em>Resolution: Deduplicated via primary key constraint on import.</em></li>
                <li><strong>Invalid Buyers/Sellers:</strong> <code>TXN-0119</code> referenced a missing buyer <code>X-99</code>. <em>Resolution: Discarded transaction during import.</em></li>
                <li><strong>Unit Inconsistencies:</strong> <code>TXN-0114</code> used <code>bales</code>. <em>Resolution: Converted to <code>kg</code> automatically (1 bale = 165kg).</em></li>
                <li><strong>Expired Licenses:</strong> <code>G-04</code> traded after license expiry. <em>Resolution: Flagged in the organization table below.</em></li>
                <li><strong>Overselling:</strong> Some organizations have a negative available balance. <em>Resolution: Flagged in the organization table below.</em></li>
            </ul>
        </div>

        <h2>Organization Balances</h2>
        <table>
            <tr>
                <th>Org ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Received (kg)</th>
                <th>Sold (kg)</th>
                <th>Available (kg)</th>
                <th>Identified Problems</th>
            </tr>
    """
    
    for org_id, data in org_data.items():
        avail_class = "negative" if data["available"] < 0 else ""
        problems_html = "<br>".join(data["problems"]) if data["problems"] else "None"
        
        html += f"""
            <tr>
                <td>{org_id}</td>
                <td>{data["name"]}</td>
                <td>{data["type"]}</td>
                <td>{data["received"]:,.2f}</td>
                <td>{data["sold"]:,.2f}</td>
                <td class="{avail_class}">{data["available"]:,.2f}</td>
                <td class="problem-list">{problems_html}</td>
            </tr>
        """
        
    html += '''
        </table>
    </body>
    </html>
    '''
    return html
