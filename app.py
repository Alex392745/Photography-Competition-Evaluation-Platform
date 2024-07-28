import hashlib
import json
import os
import random
import secrets
import sqlite3
import uuid
from datetime import datetime

from flask import Flask, request, send_file, render_template
from flask_apscheduler import APScheduler


app = Flask(__name__)
database = "database.db"

begin_day=(2024,7,28)

session = []
session_find = {}

def load_users():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT uid,password FROM user")
    users = cursor.fetchall()
    conn.close()
    return users

def update_session():
    users = load_users()
    for username, password in users:
        session.append(password)
        session_find[password] = username

def get_day():
    begin_date = datetime(*begin_day)
    return (datetime.now() - begin_date).days+1

def get_unix_time():
    return int(datetime.now().timestamp())

@app.route("/api/v1/session/verify", methods=["GET"])
def session_verify():
    update_session()
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 400, "success": False, "data": {"message": "Invalid request"}}
    if session_id in session:
        return {
            "code": 200,
            "success": True,
        }
    else:
        return {
            "code": 401,
            "success": False,
            "data": {"message": "Invalid session ID"},
        }

@app.route("/api/v1/com/list", methods=["GET"])
def com_list():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT uid, day{} FROM uservote".format(get_day()))
    result = cursor.fetchall()
    conn.close()
    return {"code": 200, "success": True, "data": result}

@app.route("/api/v1/com/query", methods=["GET"])
def com_query():
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 400, "success": False, "data": {"message": "Invalid request"}}
    uid=session_find.get(session_id)
    if not uid:
        return {"code": 401, "success": False, "data": {"message": "Invalid session ID"}}
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT day{} FROM uservote WHERE uid=?".format(get_day()), (uid,))
    result = cursor.fetchone()
    conn.close()
    return {"code": 200, "success": True, "uid": uid,"data": result[0]}

@app.route("/api/v1/day", methods=["GET"])
def day():
    return {"code": 200, "success": True, "data": get_day()}

@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon/favicon.ico", mimetype="image/vnd.microsoft.icon")


@app.route("/")
def index():
    return render_template("index.html")


crontab = APScheduler()
crontab.init_app(app)
crontab.start()


if __name__ == "__main__":
    app.run()
