from flask import Blueprint, request, jsonify, make_response, current_app
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import uuid
import jwt

from extensions import db
from models import User

auth_blueprint = Blueprint('auth_blueprint', __name__)

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
        # print(token)
        
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            current_user = User.query\
                .filter_by(public_id = data['public_id'])\
                .first()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated

# User Database Route
# this route sends back list of users
@auth_blueprint.route('/user', methods =['GET'])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json 
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name' : user.name,
            'email' : user.email
        })
  
    return jsonify({'users': output})

# route for logging user in
@auth_blueprint.route('/login', methods =['POST'])
def login():
    # creates dictionary of form data
    auth = request.json

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return jsonify({
                'message' : 'email and password are required'
            }), 401
  
    user = User.query\
        .filter_by(email = auth.get('email'))\
        .first()
  
    if not user:
        # returns 401 if user does not exist
        return jsonify({
                'message' : 'User does not exist'
            }), 401
  
    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.now(timezone.utc) + timedelta(minutes = 30)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
  
        response = {
            'user': {
                'username': user.username,
                'email': user.email,
                'roles': user.roles,
                'public_id': user.public_id
            },
            'token' : token
        }

        return make_response(jsonify(response), 201)
    
    # returns 403 if password is wrong
    return jsonify({
                'message' : 'Wrong password'
            }), 401

# signup route
@auth_blueprint.route('/signup', methods =['POST'])
def signup():
    # creates a dictionary of the form data
    data = request.json

    # gets name, email and password
    username, email = data.get('username'), data.get('email')
    password = data.get('password')

    if username == None or email == None or password == None:
        return jsonify({
                'message' : 'username, email, and password cannot be null/None'
            }), 400
    if len(username) == 0 or len(email) == 0 or len(password) == 0:
        return jsonify({
                'message' : 'username, email, and password cannot be empty'
            }), 400

    # checking for existing user
    user = User.query\
        .filter_by(email = email)\
        .first()
    if not user:
        # database ORM object
        user = User(
            public_id = str(uuid.uuid4()),
            username = username,
            email = email,
            password = generate_password_hash(password),
            roles = 'ROLE_USER',
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.now(timezone.utc) + timedelta(minutes = 30)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        response = {
            'user': {
                'username': user.username,
                'email': user.email,
                'roles': user.roles,
                'public_id': user.public_id
            },
            'token' : token
        }

        return make_response(jsonify(response), 201)
    else:
        # returns 202 if user already exists
        return jsonify({
                'message' : 'User already exists.'
            }), 202