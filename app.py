from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def user():
	user_id = request.args.get("id")

	connection = sqlite3.connect("sqli_lab.db")
	cursor = connection.cursor()

	query = "SELECT * FROM users WHERE id = " + user_id
	print("SQL QUERY:", query)
	cursor.execute(query)

	result = cursor.fetchone()

	connection.close()

	if result:
		return str(result)

	return "User not found"

@app.route("/blind")
def blind():
	blind_id = request.args.get("id")

	connection = sqlite3.connect("sqli_lab.db")
	cursor = connection.cursor()

	query = "SELECT * FROM users WHERE id = " + blind_id
	print("SQL QUERY:", query)

	cursor.execute(query)

	result = cursor.fetchone()

	connection.close()

	if result:
		return "User exists"

	return "User not found"

@app.route("/search")
def search():
	search_term = request.args.get("q")

	connection = sqlite3.connect("sqli_lab.db")
	cursor = connection.cursor()

	query = "SELECT name, description FROM products WHERE name LIKE ?"
	print("SQL QUERY:", query)

	cursor.execute(query, ("%" + search_term + "%",))

	results = cursor.fetchall()

	connection.close()

	if results:
		return "<br>".join(str(result) for result in results)

	return "No products found"

if __name__ == "__main__":
	app.run(debug=True)
