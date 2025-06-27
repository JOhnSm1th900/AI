import mysql.connector

db = mysql.connector.connect(host='localhost', user='root', password='', database='sakila')

cursor = db.cursor()

name = 'JOHN',

cursor.execute('SELECT first_name,last_name FROM actor WHERE first_name = %s', name)

results = cursor.fetchall()

for result in results:
    print(result)
