from flask import Blueprint, request, jsonify, make_response
import uuid

from extensions import db, es_client
from models import User, Collection, CollectionItem

collection_blueprint = Blueprint('collection_blueprint', __name__)

# route for getting collections by user_id
@collection_blueprint.route('/get_collections_by_user_id', methods =['POST'])
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
                content = es_client.search(index='bgg', query={
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
@collection_blueprint.route('/get_collection_by_public_id', methods =['POST'])
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
        content = es_client.search(index='bgg', query={
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
        rec_list = es_client.search(index='bgg', query={
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
@collection_blueprint.route('/create_collection', methods =['POST'])
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
@collection_blueprint.route('/delete_collection', methods =['POST'])
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
@collection_blueprint.route('/get_collections_to_add', methods =['GET'])
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
    

@collection_blueprint.route('/add_item', methods =['POST'])
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

@collection_blueprint.route('/delete_item', methods =['POST'])
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