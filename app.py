import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g
from create_db import hash_pass

from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address

import pyotp
import time
from flask_mail import Mail, Message

app = Flask(__name__)
app.database = "db.sqlite"
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://"
)

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587  # Use the appropriate port for your email server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'  # Set your default sender email
app.config['MAIL_SUPPRESS_SEND'] = False  # Set to True during development to suppress sending emails

mail = Mail(app)

totp = pyotp.TOTP('base32secret3232')


@app.errorhandler(RateLimitExceeded)
def ratelimit_error(e):
    return jsonify(error="ratelimit exceeded", message=str(e.description)), 429


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Adjust the rate limit as needed
@limiter.limit("50 per day")  # Adjust the rate limit as needed
def loginAPI():
    if request.method == 'POST':
        uname, email, pword, code = (
            request.json['username'],
            request.json['email'],
            request.json['password'],
            request.json['code']  # Get the TOTP code from the request
        )

        # Generate and send TOTP code via email
        totp_code = totp.now()
        send_totp_email(uname, email, totp_code)

        # Check TOTP
        if not totp.verify(code):  # Verify the user-entered TOTP code
            return jsonify({'status': 'totp_fail'}), 401

        g.db = connect_db()

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
            g.db.execute("INSERT INTO failed_logins (username, attempts, last_attempt) VALUES (?, 1, ?)",
                         (uname, time.time()))
            g.db.commit()
            result = {'status': 'fail'}

        g.db.close()
        return jsonify(result)


def send_totp_email(username, email, totp_code):
    subject = 'Your Two-Factor Authentication Code'
    body = f'Hello {username},\n\nYour two-factor authentication code is: {totp_code}'

    msg = Message(subject, recipients=[f'{email}'])
    msg.body = body

    try:
        mail.send(msg)
    except Exception as e:
        print(f'Error sending email: {e}')


@app.route('/restock')
def restock():
    return render_template('restock.html')


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
