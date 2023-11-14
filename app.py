import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g

from create_db import hash_pass

app = Flask(__name__)
app.database = "db.sqlite"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/restock')
def restock():
    return render_template('restock.html')


# API routes
@app.route('/api/v1.0/storeLoginAPI/', methods=['POST'])
def loginAPI():
    if request.method == 'POST':
        uname, pword = (request.json['username'], request.json['password'])
        g.db = connect_db()
        cur = g.db.execute(
            "SELECT * FROM employees WHERE username = '%s' AND password = '%s'" % (uname, hash_pass(pword)))
        if cur.fetchone():
            result = {'status': 'success'}
        else:
            result = {'status': 'fail'}
        g.db.close()
        return jsonify(result)


@app.route('/api/v1.0/storeAPI', methods=['GET', 'POST'])
def storeapi():
    if request.method == 'GET':
        g.db = connect_db()
        curs = g.db.execute("SELECT * FROM shop_items")
        cur2 = g.db.execute("SELECT * FROM employees")
        items = [{'items': [dict(name=row[0], quantity=row[1], price=row[2]) for row in curs.fetchall()]}]
        empls = [{'employees': [dict(username=row[0], password=row[1]) for row in cur2.fetchall()]}]
        g.db.close()
        return jsonify(items + empls)

    elif request.method == 'POST':
        g.db = connect_db()
        name, quan, price = (request.json['name'], request.json['quantity'], request.json['price'])
        curs = g.db.execute("""INSERT INTO shop_items(name, quantity, price) VALUES(?,?,?)""", (name, quan, price))
        g.db.commit()
        g.db.close()
        return jsonify({'status': 'OK', 'name': name, 'quantity': quan, 'price': price})


@app.route('/api/v1.0/storeAPI/<item>', methods=['GET'])
def searchAPI(item):
    g.db = connect_db()
    # curs = g.db.execute("SELECT * FROM shop_items WHERE name=?", item) #The safe way to actually get data from db
    curs = g.db.execute("SELECT * FROM shop_items WHERE name = '%s'" % item)
    results = [dict(name=row[0], quantity=row[1], price=row[2]) for row in curs.fetchall()]
    g.db.close()
    return jsonify(results)


@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('error.html', error=error)


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error=error)


def connect_db():
    return sqlite3.connect(app.database)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
