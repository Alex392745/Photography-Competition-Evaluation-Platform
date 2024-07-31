import hashlib
import json
import os
import random
import secrets
import sqlite3
import uuid
from datetime import datetime

from flask import Flask, request, send_file, render_template



app = Flask(__name__)
database = "database.db"

begin_day=(2024,7,29)

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

@app.route("/api/v1/com/info", methods=["POST"])
def com_info():
    update_session()
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 403, "success": False, "data": {"message": "Invalid request"}}
    uid=session_find.get(session_id)
    if not uid:
        return {"code": 401, "success": False, "data": {"message": "Invalid session ID"}}
    data = request.json
    cid=data.get("cid")
    if not data:
        return {"code": 400, "success": False, "data": {"message": "Invalid request"}}
    
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if(uid==1): 
        cursor.execute("SELECT vote1 FROM cvote WHERE cid=?", (cid,))
    if(uid==2): 
        cursor.execute("SELECT vote2 FROM cvote WHERE cid=?", (cid,))
    if(uid==3):
        cursor.execute("SELECT vote3 FROM cvote WHERE cid=?", (cid,))
    if(uid==4):
        cursor.execute("SELECT vote4 FROM cvote WHERE cid=?", (cid,))
    if(uid==5):
        cursor.execute("SELECT vote5 FROM cvote WHERE cid=?", (cid,))
    if(uid==6):
        cursor.execute("SELECT vote6 FROM cvote WHERE cid=?", (cid,))
    if(uid==7):
        cursor.execute("SELECT vote7 FROM cvote WHERE cid=?", (cid,))
    if(uid==8):
        cursor.execute("SELECT vote8 FROM cvote WHERE cid=?", (cid,))
    result = cursor.fetchone()
    conn.close()

    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM uploads WHERE cid=?", (cid,))
    path = cursor.fetchone()
    conn.close()

    return {"code": 200, "success": True, "data": result, "path": path}


@app.route("/api/v1/vote/query", methods=["POST"])
def vote_query():
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 400, "success": False, "data": {"message": "Invalid request"}}
    uid=session_find.get(session_id)
    if not uid:
        return {"code": 401, "success": False, "data": {"message": "Invalid session ID"}}
    data = request.json
    cid=data.get("cid")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    print(cursor.execute("SELECT vote{} FROM cvote WHERE cid=?".format(uid), (cid,)).fetchone()[0])
    if(cursor.execute("SELECT vote{} FROM cvote WHERE cid=?".format(uid), (cid,)).fetchone()[0]==-1):
        cursor.execute("UPDATE cvote SET vote{} = 0 WHERE cid=?".format(uid), (cid,))
        cursor.execute("UPDATE uservote SET day{} = day{} + 1 WHERE uid=?".format(get_day(), get_day()), (uid,))
        conn.commit()
    cursor.execute("SELECT vote{} FROM cvote WHERE cid=? ".format(uid), (cid,))
    result = cursor.fetchall()
    print(result)
    conn.close()
    return {"code": 200, "success": True, "data": result}

@app.route("/api/v1/vote/vote", methods=["POST"])
def vote_vote():
    flag=0
    update_session()
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 403, "success": False, "data": {"message": "Invalid request"}}
    uid=session_find.get(session_id)
    if not uid:
        return {"code": 401, "success": False, "data": {"message": "Invalid session ID"}}
    data = request.json
    cid=data.get("cid")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if(uid==1):
        if(cursor.execute("SELECT vote1 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote1 = 1 WHERE cid=?", (cid,))
    if(uid==2):
        if(cursor.execute("SELECT vote2 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote2 = 1 WHERE cid=?", (cid,))
    if(uid==3):
        if(cursor.execute("SELECT vote3 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote3 = 1 WHERE cid=?", (cid,))
    if(uid==4):
        if(cursor.execute("SELECT vote4 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote4 = 1 WHERE cid=?", (cid,))
    if(uid==5):
        if(cursor.execute("SELECT vote5 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote5 = 1 WHERE cid=?", (cid,))
    if(uid==6):
        if(cursor.execute("SELECT vote6 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote6 = 1 WHERE cid=?", (cid,))
    if(uid==7):
        if(cursor.execute("SELECT vote7 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote7 = 1 WHERE cid=?", (cid,))
    if(uid==8):
        if(cursor.execute("SELECT vote8 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote8 = 1 WHERE cid=?", (cid,))
    conn.commit()
    conn.close()
    return {"code": 200, "success": True}

@app.route("/api/v1/vote/cancel", methods=["POST"])
def vote_cancel():
    flag=0
    update_session()
    try:
        session_id = request.headers["X-Session-ID"]
    except KeyError:
        return {"code": 403, "success": False, "data": {"message": "Invalid request"}}
    uid=session_find.get(session_id)
    if not uid:
        return {"code": 401, "success": False, "data": {"message": "Invalid session ID"}}
    data = request.json
    cid=data.get("cid")
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if(uid==1):
        if(cursor.execute("SELECT vote1 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote1 = 0 WHERE cid=?", (cid,))
    if(uid==2):
        if(cursor.execute("SELECT vote2 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote2 = 0 WHERE cid=?", (cid,))
    if(uid==3):
        if(cursor.execute("SELECT vote3 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote3 = 0 WHERE cid=?", (cid,))
    if(uid==4):
        if(cursor.execute("SELECT vote4 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote4 = 0 WHERE cid=?", (cid,))
    if(uid==5):
        if(cursor.execute("SELECT vote5 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote5 = 0 WHERE cid=?", (cid,))
    if(uid==6):
        if(cursor.execute("SELECT vote6 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote6 = 0 WHERE cid=?", (cid,))
    if(uid==7):
        if(cursor.execute("SELECT vote7 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote7 = 0 WHERE cid=?", (cid,))
    if(uid==8):
        if(cursor.execute("SELECT vote8 FROM cvote WHERE cid=?", (cid,)).fetchone()[0]==-1):
            flag=1
        cursor.execute("UPDATE cvote SET vote8 = 0 WHERE cid=?", (cid,))
    conn.commit()
    conn.close()
    return {"code": 200, "success": True}



@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon/favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file("uploads/"+filename, mimetype="image/vnd.microsoft.icon")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/evaluation/<cid>")
def evaluation(cid):
    return render_template("evaluation.html", cid=cid)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
