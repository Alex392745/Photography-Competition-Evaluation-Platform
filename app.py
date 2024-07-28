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

session = {}
downloads_tasks = {}


def get_unix_time():
    return int(datetime.now().timestamp())


@app.route("/api/v1/user/login", methods=["POST"])
def user_login():
    try:
        username = request.json["username"]
        password = request.json["password"]
    except KeyError:
        return {
            "code": 400,
            "success": False,
            "data": {"message": "Invalid request"},
        }
    password = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, password)
    )
    user = c.fetchone()
    conn.close()
    if user:
        session_id = uuid.uuid4().hex
        session[session_id] = {
            "uid": user[0],
            "username": user[1],
            "login_time": datetime.now().timestamp(),
        }
        return {
            "code": 200,
            "success": True,
            "data": {
                "session_id": session_id,
                "uid": user[0],
                "username": user[1],
                "group": user[3],
            },
        }
    else:
        return {
            "code": 404,
            "success": False,
            "data": {"message": "Invalid username or password"},
        }


@app.route("/api/v1/user/logout", methods=["POST"])
def user_logout():
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {
            "code": 400,
            "success": False,
            "data": {"message": "Invalid request "},
        }
    if session_id in session:
        del session[session_id]
        return {"code": 200, "success": True, "data": {"message": "Logged out"}}
    else:
        return {
            "code": 401,
            "success": False,
            "data": {"message": "Invalid session ID"},
        }


@app.route("/api/v1/session/verify", methods=["GET"])
def session_verify():
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 400, "success": False, "data": {"message": "Invalid request"}}
    if session_id in session:
        return {
            "code": 200,
            "success": True,
            "data": {
                "uid": session[session_id]["uid"],
                "username": session[session_id]["username"],
            },
        }
    else:
        return {
            "code": 401,
            "success": False,
            "data": {"message": "Invalid session ID"},
        }


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
