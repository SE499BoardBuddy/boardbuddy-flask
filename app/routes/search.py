from flask import Blueprint, request, jsonify
import pandas as pd

from extensions import es_client
from functions.build_filter import *

search_blueprint = Blueprint('search_blueprint', __name__)

def get_categories():
    categories_list = []
    result = es_client.search(index='bgg', aggs= {
        "categories": {
            "terms": {
                "field": "boardgame_subdomain.keyword"
            }
        }
    })['aggregations']['categories']['buckets']
    for key in result:
        categories_list.append(key['key'])
    return categories_list

@search_blueprint.route('/search', methods=['GET'])
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
        results = es_client.search(index='bgg', query={
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
        results = es_client.search(index='bgg', query={
                "bool":{
                    "must": match_query,
                    "filter": filter_query
                }
            }, suggest_field='name', suggest_text=query_term, suggest_mode='missing', from_=page, size=size)
    
    index_key = es_client.search(index='bgg', query={
        "bool" : {
            "must" : {
                "match_all": {},
            },
        },
    }, size=1)['hits']['hits'][0]['_source']
    index_key_list = [key for key in index_key.keys()]

    total_hit = results['hits']['total']['value']
    results_df = pd.DataFrame([[hit['_source'][key] for key in hit['_source']] for hit in results['hits']['hits']], columns=index_key_list)
    results_df['_score'] = [hit['_score'] for hit in results['hits']['hits']]
    response_object['total_hit'] = total_hit
    response_object['results'] = results_df.to_dict('records')
    response_object['suggest'] = results['suggest']
    response_object['categories'] = get_categories()
    return response_object

@search_blueprint.route('/boardgame/<bg_id>', methods =['GET'])
def get_bg_by_id(bg_id=0):
    try:
        int(bg_id)
    except:
        return jsonify({'message' : 'bg_id must be a number'}), 400
    
    bg = es_client.search(index='bgg', query={
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
        rec_list = es_client.search(index='bgg', size=4, query={
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