# flask imports
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid # for public id
from  werkzeug.security import generate_password_hash, check_password_hash
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask_cors import CORS
import os
from dotenv import load_dotenv

from elasticsearch import Elasticsearch
import pandas as pd

import random

from langchain_community.embeddings import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_qdrant import QdrantVectorStore

from build_filter import build_filter_min_age, build_filter_min_players, build_filter_max_players, build_filter_match
from build_filter import build_filter_min_playtime, build_filter_max_playtime, build_filter_min_year, build_filter_max_year
from pick_filter import pick_filter_min_age, pick_filter_min_playtime, pick_filter_max_playtime
from pick_filter import pick_filter_min_players, pick_filter_max_players

load_dotenv(override=True)

# creates Flask object
app = Flask(__name__)
CORS(app)
# configuration
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://'+os.environ.get('MYSQL_USERNAME')+':'+os.environ.get('MYSQL_PASSWORD')+'@'+os.environ.get('MYSQL_URL')+'/boardbuddy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)

app.es_client = Elasticsearch("https://localhost:9200", basic_auth=("elastic", os.environ.get('ELASTIC_KEY')), ca_certs="~/http_ca.crt")
app.df = pd.read_parquet('bgg_games_info_cleaned.parquet.gzip')

# embedding
app.embeddings = OllamaEmbeddings(model='nomic-embed-text') 

# qdrant
app.qdrant = QdrantVectorStore.from_existing_collection(
    embedding=app.embeddings,
    collection_name="brass_birmingham",
    url="https://183e03de-cba4-4c31-9a62-be25dc87e60e.europe-west3-0.gcp.cloud.qdrant.io",
    api_key=os.environ["QDRANT_KEY"],
)
app.retriever=app.qdrant.as_retriever()

# llm
app.llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.environ["GOOGLE_API_KEY_GEN"])

# Database ORMs
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(70), unique = True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    roles = db.Column(db.String(100), nullable=False)
    collections = db.relationship('Collection', backref='user', lazy=True, cascade="all,delete")
    chats = db.relationship('ChatHistory', backref='user', lazy=True, cascade="all,delete")

class Collection(db.Model):
    __tablename__ = "collection"
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), nullable=False)
    boardgames = db.relationship('CollectionItem', backref='collection', lazy=True, cascade="all,delete")

class CollectionItem(db.Model):
    __tablename__ = "item"
    # id = db.Column(db.Integer, primary_key = True)
    bg_id = db.Column(db.Integer, nullable=False)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    collection_id = db.Column(db.String(50), db.ForeignKey('collection.public_id'), nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint(
            bg_id, collection_id,
        ),
    )

class ChatHistory(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    game = db.Column(db.Integer, nullable=False)
    chats = db.relationship('ChatMessage', backref='history', lazy=True, cascade="all,delete")

class ChatMessage(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    chat_id = db.Column(db.String(50), db.ForeignKey('history.public_id'), nullable=False)
    is_human = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text, nullable=False)

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
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
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
@app.route('/user', methods =['GET'])
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

# route for getting collections by user_id
@app.route('/get_collections_by_user_id', methods =['POST'])
def get_collections_by_user_id():
    # creates dictionary of form data
    req = request.json
  
    collections = Collection.query\
        .filter_by(user_id = req.get('user_id'))\
        .all()
  
    output = []
    for collection in collections:
        game_count = 0
        thumbnail = []
    
        items = CollectionItem.query\
            .filter_by(collection_id = collection.public_id)\
            .all()
  
        for item in items:
            if game_count <= 2:
                content = app.es_client.search(index='bgg', query={
                        "constant_score" : { 
                                "filter" : {
                                    "term" : { 
                                        "id" : item.bg_id
                                    }
                                }
                            }
                    })['hits']['hits']
                if len(content) != 0:
                    item_content = content[0]["_source"]
                    thumbnail.append(item_content['image'])
            game_count = game_count + 1
            
        # append 
        # to the response list
        output.append({
            'name': collection.name,
            'public_id': collection.public_id,
            'game_count': game_count,
            'thumbnail': thumbnail
        })
  
    return jsonify(output)

# route for getting collection items by public_id
@app.route('/get_collection_by_public_id', methods =['POST'])
def get_collection_by_public_id():
    # creates dictionary of form data
    req = request.json
  
    items = CollectionItem.query\
        .filter_by(collection_id = req.get('collection_id'))\
        .all()
  
    collection = Collection.query\
        .filter_by(public_id = req.get('collection_id'))\
        .first()
    
    if not collection or collection.user_id != req.get('user_id'):
        return jsonify({'message' : 'Collection not found'}), 404
    
    es_id = []
    output = []
    for item in items:
        # append 
        # to the response list
        content = app.es_client.search(index='bgg', query={
                "constant_score" : { 
                        "filter" : {
                            "term" : { 
                                "id" : item.bg_id
                            }
                        }
                    }
            })['hits']['hits'][0]
        output.append({
            'bg_id': item.bg_id,
            'public_id': item.public_id,
            'name': content["_source"]['name'],
            'image': content["_source"]['image'],
        })
        es_id.append({
            '_id': content['_id'],
        })

    rec_list = []
    if len(es_id) != 0:
        rec_list = app.es_client.search(index='bgg', query={
                "more_like_this": {
                    "fields": ["name", "description", "boardgame_subdomain"],
                    "like": es_id,
                    "min_term_freq": 1,
                    "min_doc_freq": 5,
                    "max_query_terms": 20
            }
        })['hits']['hits']

    rec_bg_list = []
    for i in rec_list:
        rec_bg_list.append({
            '_id': i['_id'],
            'bg_id': i['_source']['id'],
            'name': i['_source']['name'],
            'image': i['_source']['image']
        })
    
    response = {
        'name': collection.name,
        'public_id': collection.public_id,
        'items': output,
        'recommendation': rec_bg_list
    }
  
    return jsonify(response)

# route for getting collection items by public_id
@app.route('/create_collection', methods =['POST'])
def create_collection():
    # creates dictionary of form data
    data = request.json
    name = data.get('name')
    user_id = data.get('user_id')

    user = User.query\
        .filter_by(public_id = user_id)\
        .first()
    
    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
    
    new_collection = Collection(
        name = name,
        public_id = str(uuid.uuid4()),
    )
    user.collections.append(new_collection)
    db.session.add(new_collection)
    db.session.commit()
    return make_response('create collection')

# route for getting collection items by public_id
@app.route('/delete_collection', methods =['POST'])
def delete_collection():
    # creates dictionary of form data
    data = request.json
    public_id = data.get('public_id')

    collection = Collection.query\
        .filter_by(public_id = public_id)\
        .first()
    
    if not collection:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Collection does not exist !!"'}
        )

    db.session.delete(collection)
    db.session.commit()
    return make_response('delete collection')

# route for getting collections by user_id
@app.route('/get_collections_to_add', methods =['GET'])
def get_collections_to_add():
    # creates dictionary of form data
    user_id = request.args.get('user_id')
    bg_id = request.args.get('bg_id')

    collections = Collection.query\
        .filter_by(user_id = user_id)\
        .all()
    
    output = []
    for collection in collections:
        have = False
        items = CollectionItem.query\
            .filter_by(
                bg_id = bg_id,
                collection_id = collection.public_id
            )\
            .all()
        
        if len(items) != 0:
            have = True

        output.append({
            'name': collection.name,
            'public_id': collection.public_id,
            'have': have
        })
    
    response = {
        'collections': output,
    }
    return jsonify(response), 200
    

@app.route('/add_item', methods =['POST'])
def add_item():
    # creates dictionary of form data
    data = request.json
    bg_id = data.get('bg_id')
    collection_id = data.get('collection_id')

    collection = Collection.query\
        .filter_by(public_id = collection_id)\
        .first()

    if not collection:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
    else:
        item = CollectionItem.query\
            .filter_by(bg_id = bg_id, collection_id = collection.public_id)\
            .first()
        if not item:
            new_item = CollectionItem(
                bg_id = bg_id,
                public_id = str(uuid.uuid4()),
            )
            collection.boardgames.append(new_item)
            db.session.add(new_item)
            db.session.commit()
            return make_response('add item')
        else:
            return jsonify({
                'message' : 'Duplicated entry'
            }), 403

@app.route('/delete_item', methods =['POST'])
def delete_item():
    # creates dictionary of form data
    data = request.json
    public_id = data.get('public_id')

    item = CollectionItem.query\
        .filter_by(public_id = public_id)\
        .first()
    
    if not item:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Collection does not exist !!"'}
        )

    db.session.delete(item)
    db.session.commit()
    return make_response('delete item')

# route for logging user in
@app.route('/login', methods =['POST'])
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
        }, app.config['SECRET_KEY'], algorithm="HS256")
  
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
@app.route('/signup', methods =['POST'])
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
        }, app.config['SECRET_KEY'], algorithm="HS256")

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

@app.route('/search', methods=['GET'])
def search_recipes():
    response_object = {'status':200}
    #for query
    query_term = request.args.get('query')
    size = request.args.get('size')
    page = request.args.get('page')

    if request.args.get('query') == None:
        return jsonify({
                'message' : 'query is required'
            }), 400
    
    if size == None or len(size) == 0:
        size = 32
    else:
        size = int(size)

    if page == None or len(page) == 0:
        page = 0
    else:
        if (int(page) - 1) * size <= 0:
            page = 0
        else: 
            page = (int(page) - 1) * size

    #for filters
    #age
    min_age = request.args.get('mnage')
    #players
    min_players = request.args.get('mnpl')
    max_players = request.args.get('mxpl')
    #playtime
    min_playtime = request.args.get('mnpt')
    max_playtime = request.args.get('mxpt')
    #years
    min_year = request.args.get('mnyr')
    max_year = request.args.get('mxyr')
    #designer
    bg_designer = request.args.get('bgds')
    #publisher
    bg_publisher = request.args.get('bgpb')
    #subdomain
    bg_subdomain = request.args.get('bgsd')

    filter_query = []
    build_filter_min_age(filter_query, min_age)
    build_filter_min_players(filter_query, min_players)
    build_filter_max_players(filter_query, max_players)
    build_filter_min_playtime(filter_query, min_playtime)
    build_filter_max_playtime(filter_query, max_playtime)
    build_filter_min_year(filter_query, min_year)
    build_filter_max_year(filter_query, max_year)

    match_query = []
    build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain)

    results = any
    if query_term == None or len(query_term) == 0:
        results = app.es_client.search(index='bgg', query={
                "bool":{
                    "must": match_query,
                    "filter": filter_query
                }
            }, suggest_field='name', suggest_text=query_term, suggest_mode='missing', from_=page, size=size)
        
    else:
        match_query.append({
            "multi_match" : {
                "query" : query_term,
                "type" : "best_fields",
                "fields" : [ "name^3", "description" ],
                "tie_breaker": 0.3,
                "fuzziness" : "AUTO",
            }
        })
        results = app.es_client.search(index='bgg', query={
                "bool":{
                    "must": match_query,
                    "filter": filter_query
                }
            }, suggest_field='name', suggest_text=query_term, suggest_mode='missing', from_=page, size=size)
        
    total_hit = results['hits']['total']['value']
    results_df = pd.DataFrame([[hit['_source'][key] for key in hit['_source']] for hit in results['hits']['hits']], columns=list(app.df.columns))
    results_df['_score'] = [hit['_score'] for hit in results['hits']['hits']]
    response_object['total_hit'] = total_hit
    response_object['results'] = results_df.to_dict('records')
    response_object['suggest'] = results['suggest']
    response_object['categories'] = app.df['boardgame_subdomain'].unique().tolist()
    return response_object

@app.route('/boardgame/<bg_id>', methods =['GET'])
def get_bg_by_id(bg_id=0):
    try:
        int(bg_id)
    except:
        return jsonify({'message' : 'bg_id must be a number'}), 400
    
    bg = app.es_client.search(index='bgg', query={
            "constant_score" : { 
                    "filter" : {
                        "term" : { 
                            "id" : bg_id
                        }
                    }
                }
        })['hits']['hits']
    result = {}
    if len(bg) != 0:
        result = bg[0]["_source"]
        es_id = bg[0]["_id"]
        rec_list = app.es_client.search(index='bgg', size=4, query={
            "more_like_this": {
                "fields": ["name", "description", "boardgame_subdomain"],
                "like": {
                    "_id": es_id
                },
                "min_term_freq": 1,
                "min_doc_freq": 5,
                "max_query_terms": 20
            }
        })['hits']['hits']
        result["recommendation"] = rec_list
    else:
        return jsonify({'message' : 'Boardgame not found'}), 404
        
    return jsonify(result)

@app.route('/random_pick', methods =['POST'])
def random_pick():
    data = request.json
    collection_id = data.get('collection_id')
    min_age = data.get('min_age')
    min_playtime = data.get('min_playtime')
    max_playtime = data.get('max_playtime')
    min_players = data.get('min_players')
    max_players = data.get('max_players')

    collection = Collection.query\
        .filter_by(public_id = collection_id)\
        .first()
    
    items = CollectionItem.query\
        .filter_by(collection_id = collection_id)\
        .all()
    
    if not collection:
        return jsonify({'message' : 'Collection not found'}), 404
    
    return_list = []
    for item in items:
        content = app.es_client.search(index='bgg', query={
                "constant_score" : { 
                        "filter" : {
                            "term" : { 
                                "id" : item.bg_id
                            }
                        }
                    }
            })['hits']['hits'][0]
        return_list.append({
            'bg_id': item.bg_id,
            'public_id': item.public_id,
            'name': content["_source"]['name'],
            'image': content["_source"]['image'],
            'min_playtime': content["_source"]['min_playtime'],
            'max_playtime': content["_source"]['max_playtime'],
            'min_players': content["_source"]['min_players'],
            'max_players': content["_source"]['max_players'],
            'min_age': content["_source"]['age']
        })
    
    pick_filter_min_age(return_list, min_age)
    pick_filter_min_playtime(return_list, min_playtime)
    pick_filter_max_playtime(return_list, max_playtime)
    pick_filter_min_players(return_list, min_players)
    pick_filter_max_players(return_list, max_players)

    if len(return_list) != 0:
        response = [random.choice(return_list)]
    else:
        response = []

    return jsonify(response)

@app.route('/send_message', methods =['POST'])
def send_message():
    # get json variables
    data = request.json
    message = data.get('message')
    user_id = data.get('user_id')
    chat_id = data.get('chat_id')
    game = data.get('game')

    # setup llm
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=2
    )
    qa = ConversationalRetrievalChain.from_llm(
        app.llm,
        retriever=app.retriever,
        memory=memory
    )

    # find existing user
    user = User.query\
        .filter_by(public_id = user_id)\
        .first()
    # try to find existing chat history
    history = ChatHistory.query\
        .filter_by(public_id = chat_id)\
        .filter_by(game = game)\
        .first()

    if user:
        # if chat history does not exist, create it
        if not history:
            history = ChatHistory(
                public_id = str(uuid.uuid4()),
                name = datetime.now(),
                game = game,
            )
            user.chats.append(history)
            db.session.add(history)
            db.session.commit()
        elif history:
            history_list = get_history(chat_id)
            input_message = ''
            output_message = ''
            for c in history_list:
                if len(input_message) == 0:
                    if c['is_human']:
                        input_message = c['message']
                        # print(input_message)
                if len(output_message) == 0:
                    if not c['is_human']:
                        output_message = c['message']
                        # print(output_message)
                if len(input_message) != 0 and len(output_message) != 0:
                    memory.save_context({'input': input_message}, {'output': output_message})
                    input_message = ''
                    output_message = ''

            # print(memory.load_memory_variables({}))
        # save user message to database
        new_user_chat = ChatMessage(
            public_id = str(uuid.uuid4()),
            is_human = True,
            date = datetime.now(),
            message = message
        )
        history.chats.append(new_user_chat)

        # invoke llm
        result = qa.invoke(message)
        # save ai message to database
        new_ai_chat = ChatMessage(
            public_id = str(uuid.uuid4()),
            is_human = False,
            date = datetime.now(),
            message = result['answer']
        )
        history.chats.append(new_ai_chat)

        # commit to database
        db.session.add_all([new_user_chat, new_ai_chat])
        db.session.commit()
    return jsonify(result['answer'])

@app.route('/get_history/<chat_id>', methods =['GET'])
def get_history(chat_id="-1"):

    # try to find existing chat history
    history = ChatHistory.query\
        .filter_by(public_id = chat_id)\
        .first()
    
    result = []
    if history:
        chats = ChatMessage.query\
            .filter_by(chat_id = chat_id)\
            .all()
        for c in chats:
            result.append({
                "date": c.date,
                "is_human": c.is_human,
                "message": c.message
            })
    
    return result

@app.route('/get_all_history/<user_id>', methods =['GET'])
def get_all_history(user_id="-1"):

    # try to find existing chat history
    user = User.query\
        .filter_by(public_id = user_id)\
        .first()
    
    result = []
    if user:
        history = ChatHistory.query\
            .filter_by(user_id = user_id)\
            .all()
        for h in history:
            result.append({
                "name": h.name,
                "game": h.game,
                "public_id": h.public_id
            })
    
    return result

@app.route('/delete_history', methods =['POST'])
def delete_history():
    # creates dictionary of form data
    data = request.json
    public_id = data.get('public_id')

    history = ChatHistory.query\
        .filter_by(public_id = public_id)\
        .first()
    
    if not history:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Chat History does not exist !!"'}
        )

    db.session.delete(history)
    db.session.commit()
    return make_response('delete history')

if __name__ == "__main__":
    # setting debug to True enables hot reload
    # and also provides a debugger shell
    # if you hit an error while running the server
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    #     admin = User(
    #         public_id = str(uuid.uuid4()),
    #         username = 'admin',
    #         email = 'admin@admin',
    #         password = generate_password_hash('admin'),
    #         roles = 'ROLE_ADMIN'
    #     )
    #     test_collection = Collection(
    #         name = 'test',
    #         public_id = str(uuid.uuid4()),
    #     )
    #     sec = Collection(
    #         name = 'second',
    #         public_id = str(uuid.uuid4()),
    #     )
    #     thd = Collection(
    #         name = 'third',
    #         public_id = str(uuid.uuid4()),
    #     )
    #     admin.collections = [test_collection, sec, thd]
    #     item1 = CollectionItem(
    #         bg_id = 224517,
    #         public_id = str(uuid.uuid4()),
    #     )
    #     item2 = CollectionItem(
    #         bg_id = 161936,
    #         public_id = str(uuid.uuid4()),
    #     )
    #     item3 = CollectionItem(
    #         bg_id = 174430,
    #         public_id = str(uuid.uuid4()),
    #     )
    #     sec.boardgames = [item1, item2]
    #     thd.boardgames = [item3]

    #     test_history = ChatHistory(
    #         public_id = str(uuid.uuid4()),
    #         name = "test",
    #         game = 0,
    #     )
    #     admin.chats = [test_history]
    #     test_chat1 = ChatMessage(
    #         public_id = str(uuid.uuid4()),
    #         is_human = True,
    #         date = datetime.now(),
    #         message = "first"
    #     )
    #     test_chat2 = ChatMessage(
    #         public_id = str(uuid.uuid4()),
    #         is_human = False,
    #         date = datetime.now(),
    #         message = "second"
    #     )
    #     test_history.chats = [test_chat1, test_chat2]

    #     # insert user
    #     db.session.add(admin)
    #     db.session.add_all([test_collection, sec, thd, item1, item2, item3])
    #     db.session.add_all([test_history, test_chat1, test_chat2])
    #     db.session.commit()

    app.run(debug = True)