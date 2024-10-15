from flask import Blueprint, request, jsonify
import random

from extensions import es_client
from models import Collection, CollectionItem
from functions.pick_filter import *

pick_blueprint = Blueprint('pick_blueprint', __name__)

@pick_blueprint.route('/random_pick', methods =['POST'])
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
        content = es_client.search(index='bgg', query={
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
    
    return_list = pick_filter_min_age(return_list, min_age)
    return_list = pick_filter_min_playtime(return_list, min_playtime)
    return_list = pick_filter_max_playtime(return_list, max_playtime)
    return_list = pick_filter_min_players(return_list, min_players)
    return_list = pick_filter_max_players(return_list, max_players)

    if len(return_list) != 0:
        response = [random.choice(return_list)]
    else:
        response = []

    return jsonify(response)