from flask import Blueprint, jsonify

from models import Rulebook

rulebook_blueprint = Blueprint('rulebook_blueprint', __name__)

@rulebook_blueprint.route('/get_rulebooks', methods =[ 'GET' ])
def get_rulebooks():
    rulebooks = Rulebook.query.all()
    json_rulebooks = []
    for r in rulebooks:
        json_rulebooks.append({
            'id': r.id,
            'name': r.name,
            'image': r.image,
            'link': r.link
        })
    return jsonify(json_rulebooks)