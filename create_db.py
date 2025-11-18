import sqlite3
from datetime import datetime

# Connect to SQLite (creates file if it doesn't exist)
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Create the inventory table
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER,
    reorder_level INTEGER,
    last_updated TEXT
)
""")

# Sample data
products = [
    ("Sugar 1kg", "Grocery", 120, 30),
    ("Maize Flour 2kg", "Grocery", 80, 25),
    ("Cooking Oil 1L", "Grocery", 45, 20),
    ("Toilet Paper 10pk", "Household", 60, 15),
    ("Soap Bar", "Household", 150, 50),
    ("Rice 5kg", "Grocery", 70, 30),
    ("Milk 500ml", "Dairy", 200, 60),
    ("Bread", "Bakery", 90, 40),
    ("Detergent 1kg", "Household", 35, 10),
    ("Eggs Tray", "Dairy", 55, 20)
]

# Insert data
for name, category, qty, reorder in products:
    cursor.execute("""
    INSERT INTO inventory (product_name, category, quantity, reorder_level, last_updated)
    VALUES (?, ?, ?, ?, ?)
    """, (name, category, qty, reorder, datetime.now().strftime("%Y-%m-%d")))

conn.commit()
conn.close()
