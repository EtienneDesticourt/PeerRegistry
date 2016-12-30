from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import config.test as config
import user
import user_manager
import json
from ip_manager import IpManager, NoChallengeError

NO_USER_ERROR = json.dumps({'error': 'No such user.'})
EXISTING_USER_ERROR = json.dumps({'error': 'User already exists.'})
FAILED_CHALLENGE_ERROR = json.dumps({'error': 'Challenge failed.'})
NO_CHALLENGE_ERROR = json.dumps({'error': 'No existing challenge for user.'})

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}'.format(
    username=config.db_user,
    password=config.db_password,
    hostname=config.db_host,
    databasename=config.db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SECRET_KEY'] = config.secret_key
db = SQLAlchemy(app)

User = user.create_user_class(db)
users = user_manager.UserManager(db, User)
ip_manager = IpManager()

@app.route('/user', methods=['POST'])
@app.route('/user/<username>', methods=['GET'])
def user(username=None):
    if request.method == 'GET':
        user = users.get(username=username)
        if not user:
            return NO_USER_ERROR
        return json.dumps(user.to_dict())

    elif request.method == 'POST':
        user = users.get(username=request.form['username'])
        if user:
            return EXISTING_USER_ERROR
        users.add(**request.form)
        return "OK"


@app.route('/ip', methods=['POST'])
@app.route('/ip/<username>', methods=['GET'])
def ip(username=None):
    if request.method == 'GET':
        ip = ip_manager.get_ip(username)
        return json.dumps({"ip": ip})

    elif request.method == 'POST':
        try:
            username = request.form['username']
            challenge_answer = request.form['challenge']
            ip = request.form['ip']
        except KeyError:
            return "Bad Request", 400

        try:
            if ip_manager.challenge_is_correct(username, challenge_answer):
                ip_manager.update_ip(username, ip)
                return "OK"
            return FAILED_CHALLENGE_ERROR
        except NoChallengeError:
            return NO_CHALLENGE_ERROR


@app.route('/challenge/<username>', methods=['GET'])
def challenge(username):
    user = users.get(username=username)
    if not user:
        return NO_USER_ERROR
    challenge = ip_manager.create_challenge(username)
    return json.dumps({'challenge': challenge.secret})
