import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g
from create_db import hash_pass

from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address

import time

app = Flask(__name__)
app.database = "db.sqlite"
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "2 per hour"],
    storage_uri="memory://"
)


@app.errorhandler(RateLimitExceeded)
def ratelimit_error(e):
    return jsonify(error="ratelimit exceeded", message=str(e.description)), 429


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
# API routes with rate limiting
@app.route('/api/v1.0/storeLoginAPI/', methods=['POST'])
@limiter.limit("10 per hour")  # Adjust the rate limit as needed
@limiter.limit("50 per day")  # Adjust the rate limit as needed
def loginAPI():
    if request.method == 'POST':
        uname, pword = (request.json['username'], request.json['password'])
        g.db = connect_db()

        # Check if the user is in the failed login attempts table
        cur_failed_logins = g.db.execute("SELECT * FROM failed_logins WHERE username = ?", (uname,))
        failed_login_row = cur_failed_logins.fetchone()

        if failed_login_row:
            # If there are three or more consecutive failed attempts, check the timeout
            if failed_login_row['attempts'] >= 3:
                current_time = time.time()
                if current_time - failed_login_row['last_attempt'] < 300:  # 300 seconds (5 minutes) timeout
                    result = {'status': 'timeout'}
                    g.db.close()
                    return jsonify(result)

        # Check the username and password
        cur = g.db.execute(
            "SELECT * FROM employees WHERE username = ? AND password = ?",
            (uname, hash_pass(pword))
        )

        if cur.fetchone():
            # Reset failed login attempts on successful login
            g.db.execute("DELETE FROM failed_logins WHERE username = ?", (uname,))
            g.db.commit()
            result = {'status': 'success'}
        else:
            # Update or insert failed login attempts
            if failed_login_row:
                g.db.execute("UPDATE failed_logins SET attempts = attempts + 1, last_attempt = ? WHERE username = ?",
                             (current_time, uname))
            else:
                g.db.execute("INSERT INTO failed_logins (username, attempts, last_attempt) VALUES (?, 1, ?)",
                             (uname, current_time))
            g.db.commit()
            result = {'status': 'fail'}

        g.db.close()
        return jsonify(result)


@app.route('/api/v1.0/storeAPI', methods=['GET', 'POST'])
def storeapi():
    if request.method == 'GET':
        g.db = connect_db()
        curs = g.db.execute("SELECT * FROM shop_items")
        cur2 = g.db.execute("SELECT * FROM employees")
        items = [{'items': [dict(name=row[0], image=row[1], price=row[2]) for row in curs.fetchall()]}]
        empls = [{'employees': [dict(username=row[0], password=row[1]) for row in cur2.fetchall()]}]
        g.db.close()
        return jsonify(items + empls)

    elif request.method == 'POST':
        g.db = connect_db()
        name, img, price = (request.json['name'], request.json['image'], request.json['price'])
        curs = g.db.execute("""INSERT INTO shop_items(name, image, price) VALUES(?,?,?)""", (name, img, price))
        g.db.commit()
        g.db.close()
        return jsonify({'status': 'OK', 'name': name, 'image': img, 'price': price})


@app.route('/api/v1.0/storeAPI/<item>', methods=['GET'])
def searchAPI(item):
    g.db = connect_db()
    # curs = g.db.execute("SELECT * FROM shop_items WHERE name=?", item) #The safe way to actually get data from db
    curs = g.db.execute("SELECT * FROM shop_items WHERE name = '%s'" % item)
    results = [dict(name=row[0], image=row[1], price=row[2]) for row in curs.fetchall()]
    g.db.close()
    return jsonify(results)


@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('error.html', error=error)


@app.errorhandler(429)
def ratelimit_error():
    print("test")
    return render_template('error.html', error=ratelimit_error), 429

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error=error)


def connect_db():
    return sqlite3.connect(app.database)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
