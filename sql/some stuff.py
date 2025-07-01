from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error

# Database connection
try:
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root17417',
        database='sakila'
    )
except Error as e:
    print(f"Error connecting to MySQL Platform: {e}")
    db = None

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'

@app.route('/actors', methods=['GET'])
def actors():
    if db is None:
        return jsonify({'error': 'Database connection failed'}), 500
    query = 'SELECT * FROM actor'
    results = get_results(query)
    return jsonify({'actors': results})

def get_results(query, **args):
    cursor = db.cursor(dictionary=True)  # Use dictionary=True to get results as dictionaries
    cursor.execute(query, **args)
    results = cursor.fetchall()
    cursor.close()
    return results

if __name__ == '__main__':
    app.run(debug=True)