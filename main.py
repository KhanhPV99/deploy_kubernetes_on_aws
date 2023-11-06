import os
import datetime
import logging
import jwt
import functools
from flask import Flask, jsonify, request, abort

JWT_SECRET = os.environ.get('JWT_SECRET', 'KhoiVN-secret')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class Logger:
    @classmethod
    def get_logger(cls, name: str):
        logger = logging.getLogger(name=name)
        logger.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        fh = logging.FileHandler(filename="error.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

LOG = Logger.get_logger(__name__)
LOG.debug("Starting log level: %s" % LOG_LEVEL)
APP = Flask(__name__)

def require_jwt(function):
    @functools.wraps(function)
    def decorated_function(*args, **kws):
        if (not 'Authorization') in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = str.replace(str(data), 'Bearer ', '')
        try:
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except Exception:
            abort(401)
        return function(*args, **kws)
    return decorated_function

@APP.route('/', methods=['POST', 'GET'])
def health():
    return jsonify("Healthy")

@APP.route('/contents', methods=['GET'])
def decode_jwt():
    if (not 'Authorization') in request.headers:
        abort(401)
    data = request.headers['Authorization']
    token = str.replace(str(data), 'Bearer ', '')
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception:
        abort(401)

    response = {
        'exp': data['exp'],
        'email': data['email'],
        'nbf': data['nbf']
    }
    return jsonify(**response)

@APP.route('/auth', methods=['POST'])
def auth():
    request_data = request.get_json()
    email = request_data.get('email')
    password = request_data.get('password')
    if not email:
        LOG.error("No email provided")
        return jsonify({"message": "Missing parameter: email"}, 400)

    if not password:
        LOG.error("No password provided")
        return jsonify({"message": "Missing parameter: password"}, 400)

    body = {'email': email, 'password': password}
    user_data = body
    return jsonify(token=_get_jwt(user_data).decode('utf-8'))

def _get_jwt(user_data):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=2)
    payload = {
        'nbf': datetime.datetime.utcnow(),
        'exp': exp_time,
        'email': user_data['email']
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=8080, debug=True)
