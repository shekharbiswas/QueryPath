# create_dummy_db.py
import sqlite3

def create_tables():
    conn = sqlite3.connect("data/challenges.db")
    cursor = conn.cursor()

    # From day1.json, challenge 1 schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        country TEXT,
        signup_date DATE
    )
    """)
    # Sample data (optional, but good for testing)
    customers_data = [
        (1, 'Anna Schultz', 'Germany', '2022-05-15'),
        (2, 'Lukas Meier', 'Germany', '2022-08-20'),
        (3, 'John Doe', 'USA', '2023-01-10'),
        (4, 'Elena Roth', 'Germany', '2023-03-01'),
        (5, 'Marco Beck', 'Germany', '2023-06-12'),
        (6, 'Klara Mueller', 'Germany', '2023-02-25'),
        (7, 'Ben', 'UK', '2021-11-05'), # For is_premium example
        (8, 'Lucy', 'Canada', '2022-01-15') # For is_premium example
    ]
    cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?)", customers_data)


    # From day1.json, challenge 3 schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        total_amount FLOAT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)
    orders_data = [
        (101, 1, 50.0),
        (102, 2, 1200.0),
        (103, 3, 75.5),
        (104, 5, 1500.0)
    ]
    cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?,?,?)", orders_data)

    # From day1.json, challenge 4 schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        is_premium BOOLEAN
    )
    """)
    # SQLite stores booleans as 0 or 1
    users_data = [
        (1, 'Admin', 1), # True
        (2, 'Ben', 0),   # False
        (3, 'Lucy', 0),  # False
        (4, 'PremiumUser', 1) # True
    ]
    cursor.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?)", users_data)

    conn.commit()
    conn.close()
    print("Database and tables created with sample data.")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    create_tables()