import random
from datetime import datetime, timedelta
import numpy as np
import psycopg2
from psycopg2.extras import execute_batch
from database.db import DATABASE_URL

TOTAL_INVOICES = 250000
BATCH_SIZE = 5000

DEPARTMENTS = ["IT", "Engineering", "Marketing", "Operations", "Finance", "Legal"]
ITEM_CATEGORIES = ["HW", "SW", "CONSULTING", "OFFICE", "TRAVEL"]

VENDOR_NAMES = [
    "Apex Tech Solutions", "BlueRidge Logistics", "CyberGuard Systems", "Delta Industrial",
    "EcoClean Services", "Global Network Corp", "Hyperion Cloud", "Integra Soft",
    "Javelin Logistics", "Krypton Security", "Lumina Marketing", "Meridian Consulting",
    "Nexus Enterprises", "Omega Supplies", "Pioneer Data", "Quantum Dynamics",
    "Redwood Tech", "Summit Legal", "Titan Hardware", "Vertex Solutions"
]

def get_db_connection():
    conn_str = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    return psycopg2.connect(conn_str)

def generate_random_vector(dim=384):
    vec = np.random.randn(dim).astype(np.float32)
    vec /= np.linalg.norm(vec) + 1e-8
    return str(vec.tolist())

def run_synthesis():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM vendors;")
    if cur.fetchone()[0] == 0:
        print("Seeding vendors...")
        vendors_data = []
        for i, name in enumerate(VENDOR_NAMES):
            tax_id = f"US-{random.randint(10,99)}-{random.randint(1000000,9999999)}"
            bank_acc = f"ACCT-{random.randint(10000000,99999999)}"
            address = f"{random.randint(100,9999)} Business Blvd, Suite {random.randint(10,500)}, City, State"
            risk = round(random.uniform(0.0, 0.2), 2)
            if i < 3:
                risk = 0.85
            embedding = generate_random_vector(384)
            vendors_data.append((name, tax_id, bank_acc, address, risk, embedding))

        execute_batch(cur, """
            INSERT INTO vendors (name, tax_id, bank_account, address, risk_rating, embedding)
            VALUES (%s, %s, %s, %s, %s, %s::vector)
            ON CONFLICT (tax_id) DO NOTHING;
        """, vendors_data)
        conn.commit()

    cur.execute("SELECT vendor_id FROM vendors;")
    vendor_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT COUNT(*) FROM purchase_orders;")
    if cur.fetchone()[0] == 0:
        print("Seeding purchase orders...")
        po_data = []
        start_date = datetime.now() - timedelta(days=730)
        for i in range(1, 10001):
            po_number = f"PO-2024-{i:05d}"
            v_id = random.choice(vendor_ids)
            dept = random.choice(DEPARTMENTS)
            limit = round(random.uniform(5000.0, 50000.0), 2)
            issue_dt = start_date + timedelta(days=random.randint(1, 600))
            po_data.append((po_number, v_id, dept, limit, "ACTIVE", issue_dt))
            
            if len(po_data) >= 2000:
                execute_batch(cur, """
                    INSERT INTO purchase_orders (po_number, vendor_id, department_id, amount_limit, status, issue_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (po_number) DO NOTHING;
                """, po_data)
                conn.commit()
                po_data = []

    cur.execute("SELECT po_id, amount_limit, vendor_id FROM purchase_orders;")
    pos = cur.fetchall()

    print(f"Starting streaming synthesis of {TOTAL_INVOICES} invoices in batches of {BATCH_SIZE}...")
    
    invoices_inserted = 0
    while invoices_inserted < TOTAL_INVOICES:
        current_batch_size = min(BATCH_SIZE, TOTAL_INVOICES - invoices_inserted)
        invoice_rows = []
        
        for _ in range(current_batch_size):
            invoices_inserted += 1
            inv_num = f"INV-2025-{invoices_inserted:07d}"
            po = random.choice(pos)
            po_id, po_limit, v_id = po[0], po[1], po[2]
            
            inv_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            fraud_type = random.choices(
                ["NORMAL", "DUPLICATE", "SPLIT_PO", "PRICE_DRIFT", "GHOST", "CALC_DISCREPANCY"],
                weights=[0.94, 0.012, 0.012, 0.012, 0.012, 0.012],
                k=1
            )[0]

            subtotal = round(random.uniform(500.0, 9500.0), 2)
            if fraud_type == "SPLIT_PO":
                subtotal = round(random.uniform(9800.0, 9999.0), 2)
            elif fraud_type == "PRICE_DRIFT":
                subtotal = round(po_limit * random.uniform(1.3, 1.6), 2)

            tax_amount = round(subtotal * 0.08, 2)
            total_amount = round(subtotal + tax_amount, 2)
            if fraud_type == "CALC_DISCREPANCY":
                total_amount += round(random.uniform(50.0, 500.0), 2) # discrepancy between lines and total

            raw_text = f"INVOICE {inv_num} Date: {inv_date.strftime('%Y-%m-%d')} Subtotal: ${subtotal} Tax: ${tax_amount} Total: ${total_amount}"
            embedding = generate_random_vector(384)
            status = "FLAGGED" if fraud_type != "NORMAL" else "APPROVED"

            invoice_rows.append((inv_num, v_id, po_id, inv_date, subtotal, tax_amount, total_amount, raw_text, embedding, status))

        execute_batch(cur, """
            INSERT INTO invoices (invoice_number, vendor_id, po_id, invoice_date, subtotal, tax_amount, total_amount, raw_text, embedding, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s)
        """, invoice_rows)
        conn.commit()
        
        print(f"Progress: {invoices_inserted}/{TOTAL_INVOICES} invoices synthesized and inserted.")

    cur.close()
    conn.close()
    print("Data synthesis pipeline completed successfully!")

if __name__ == "__main__":
    run_synthesis()
