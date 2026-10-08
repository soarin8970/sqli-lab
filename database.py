import sqlite3

connection = sqlite3.connect("sqli_lab.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY,
	username TEXT,
	email TEXT,
	role TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO users (id, username, email, role)
VALUES
	(1, 'alice', 'alice@example.com', 'user'),
	(2, 'bob', 'bob@example.com', 'user'),
	(3, 'admin', 'admin@example.com', 'admin')
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
	id INTEGER PRIMARY KEY,
	name TEXT,
	description TEXT,
	price REAL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO products (id, name, description, price)
VALUES
	(1, 'Laptop', 'A basic laptop', 799.99),
	(2, 'Keyboard', 'Mechanical keyboard', 89.99),
	(3, 'Mouse', 'Wireless mouse', 39.99),
	(4, 'Monitor', '27 inch monitor', 249.99)
""")

connection.commit()
connection.close()

print("Database created successfully.")
