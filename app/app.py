import json
import requests
import hashlib
import base64
import random
import time

from flask import Flask, request
from flask.wrappers import Response
from mongoDB import MongoDB

app = Flask(__name__)

users = {
    'YCH': ['123456'],
    'GYY': ['12345']
}

Administrator='YCH'

Authority_status = 0


def get_md5(token):
    md = hashlib.md5()
    md.update(token.encode('utf-8'))
    return md.digest()


def gen_hash_token(uid):
    s1 = ':'.join([uid, str(random.random()), str(time.time() + 72000)])
    token = base64.b64encode(s1.encode('utf-8'))
    users[uid].append(token)
    return token


def verify_token(token):
    _token = base64.b64decode(token)
    _token1 = _token.decode('utf-8')
    uid_name = _token1.split(':')[0]
    if not users.get(_token1.split(':')[0])[-1] == token:
        return "The token is not correct or matches your uid "
    if float(_token1.split(':')[-1]) >= time.time():
        return 1,uid_name
    else:
        return "The token has timed out"


@app.route("/index")
def index():
    global Authority_status
    if Authority_status == 1 or Authority_status == 2:
        return "This is mini-project for ECS781 group 10"
    else:
        return "Please login"


@app.route("/apply_token", methods=["POST", "GET"])  # 把token写入字典uid后面
def apply_token():
    r1 = request.headers['Authorization'].split(' ')[-1]
    r2 = base64.b64decode(r1)
    uid, pw = r2.split(b':')
    uid1 = uid.decode('utf-8')
    pw1 = pw.decode('utf-8')
    if users.get(uid1)[0] == pw1:
        return gen_hash_token(uid1)
    else:
        return 'Wrong uid or password'


@app.route("/login", methods=["POST", "GET"])
def login():
    global Administrator
    global Authority_status
    token = request.args.get("token").encode('utf-8')
    code,name=verify_token(token)
    if code == 1 and name==Administrator:
        Authority_status = 2
        return "You have login successfully"
    elif code == 1:
        Authority_status = 1
        return "You have login successfully"
    else:
        return 'Wrong token'


@app.route("/logout", methods=["POST", "GET"])
def logout():
    global Authority_status
    if Authority_status == 1 or Authority_status == 2:
        Authority_status = 0
        return "You have logout successfully"
    else:
        return 'You have not login'


@app.route("/detail/<type>/<index>")
def detail_book(type, index):
    global Authority_status
    if Authority_status == 1 or Authority_status == 2:
        url = "https://openlibrary.org/api/books?bibkeys={}:{}&format=json".format(type, index)
        return requests.get(url).json()
    else:
        return "Please login"


@app.route("/mylibrary", methods=["GET"])
def get_books():
    global Authority_status
    if Authority_status == 1 or Authority_status == 2:
        data = request.json
        if data is None or data == {}:
            return Response(
                response=json.dumps({"Error": "Please provide connection information"}),
                status=400,
                mimetype="application/json"
            )
        new_obj = MongoDB(data)
        response = new_obj.read()
        return Response(
            response=json.dumps(response),
            status=200,
            mimetype="application/json")
    else:
        return "Please login"


@app.route("/mylibrary", methods=["POST"])
def add_book():
    global Authority_status
    if Authority_status == 2:
        data = request.json
        if data is None or data == {} or "Document" not in data:
            return Response(
                response=json.dumps({"Error": "Please provide connection information"}),
                status=400,
                mimetype="application/json"
            )
        new_obj = MongoDB(data)
        response = new_obj.write(data)
        return Response(
            response=json.dumps(response),
            status=200,
            mimetype="application/json"
        )
    elif Authority_status == 1:
        return "Not an administrator account"
    else:
        return "Please login"


@app.route("/mylibrary", methods=["PUT"])
def update_book():
    global Authority_status
    if Authority_status == 2:
        data = request.json
        if data is None or data == {} or "DataToBeUpdated" not in data:
            return Response(
                response=json.dumps({"Error": "Please provide connection information"}),
                status=400,
                mimetype="application/json"
            )
        new_obj = MongoDB(data)
        response = new_obj.update()
        return Response(
            response=json.dumps(response),
            status=200,
            mimetype="application/json"
        )
    elif Authority_status == 1:
        return "Not an administrator account"
    else:
        return "Please login"


@app.route("/mylibrary", methods=["DELETE"])
def del_book():
    global Authority_status
    if Authority_status == 2:
        data = request.json
        if data is None or data == {} or "Filter" not in data:
            return Response(
                response=json.dumps({"Error": "Please provide connection information"}),
                status=400,
                mimetype="application/json"
            )
        new_obj = MongoDB(data)
        response = new_obj.delete(data)
        return Response(
            response=json.dumps(response),
            status=200,
            mimetype="application/json"
        )
    elif Authority_status == 1:
        return "Not an administrator account"
    else:
        return "Please login"


if __name__ == "__main__":
    context = ("app/cert.pem", "app/key.pem")
    app.run(host="0.0.0.0", port="5001",debug=True, ssl_context=context)
