import hashlib
import sqlite3

def hash_pass(passw):
	m = hashlib.md5()
	m.update(passw.encode('utf-8'))
	return m.hexdigest()

def create_db():
    database = "db.sqlite"

    connection = sqlite3.connect(database)
    c = connection.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS shop_items(name TEXT, quantitiy TEXT, price TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS employees(username TEXT, password TEXT)""")
    c.execute('INSERT INTO shop_items VALUES("water", "40", "100")')
    c.execute('INSERT INTO shop_items VALUES("juice", "40", "110")')
    c.execute('INSERT INTO shop_items VALUES("candy", "100", "10")')
    c.execute('INSERT INTO employees VALUES("itsjasonh", "{}")'.format(hash_pass("badword")))
    c.execute('INSERT INTO employees VALUES("theeguy9", "{}")'.format(hash_pass("badpassword")))
    c.execute('INSERT INTO employees VALUES("newguy29", "{}")'.format(hash_pass("pass123")))
    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_db()
    print("Tables created successfully.")
