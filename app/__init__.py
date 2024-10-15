import os
from dotenv import load_dotenv
load_dotenv(override=True)

from flask import Flask
from flask_cors import CORS

from config import configs

from extensions import db, es_client
from routes.auth import auth_blueprint
from routes.collection import collection_blueprint
from routes.search import search_blueprint
from routes.pick import pick_blueprint
from routes.chat import chat_blueprint
from routes.rulebook import rulebook_blueprint

from models import User, Collection, CollectionItem, ChatHistory, ChatMessage, Rulebook
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

env_config = os.environ.get('MY_FLASK_APP_ENV')

def create_app(config=configs[env_config]):
    app = Flask(__name__)
    CORS(app)

    # init config
    app.config.from_object(config)

    # init extensions
    db.init_app(app)

    # register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(collection_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(pick_blueprint)
    app.register_blueprint(chat_blueprint)
    app.register_blueprint(rulebook_blueprint)

    # init db
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(
            public_id = str(uuid.uuid4()),
            username = 'admin',
            email = 'admin@admin',
            password = generate_password_hash('admin'),
            roles = 'ROLE_ADMIN'
        )
        test_collection = Collection(
            name = 'test',
            public_id = str(uuid.uuid4()),
        )
        sec = Collection(
            name = 'second',
            public_id = str(uuid.uuid4()),
        )
        thd = Collection(
            name = 'third',
            public_id = str(uuid.uuid4()),
        )
        admin.collections = [test_collection, sec, thd]
        item1 = CollectionItem(
            bg_id = 224517,
            public_id = str(uuid.uuid4()),
        )
        item2 = CollectionItem(
            bg_id = 161936,
            public_id = str(uuid.uuid4()),
        )
        item3 = CollectionItem(
            bg_id = 174430,
            public_id = str(uuid.uuid4()),
        )
        sec.boardgames = [item1, item2]
        thd.boardgames = [item3]
        test_history = ChatHistory(
            public_id = str(uuid.uuid4()),
            name = "test",
            game = 1
        )
        admin.chats = [test_history]
        test_chat1 = ChatMessage(
            public_id = str(uuid.uuid4()),
            is_human = True,
            date = datetime.now(),
            message = "first"
        )
        test_chat2 = ChatMessage(
            public_id = str(uuid.uuid4()),
            is_human = False,
            date = datetime.now(),
            message = "second"
        )
        test_history.chats = [test_chat1, test_chat2]
        rule1 = Rulebook(
            name = 'Brass: Birmingham (2018)',
            qdrant = 'brass_birmingham',
            image = 'https://cf.geekdo-images.com/x3zxjr-Vw5iU4yDPg70Jgw__original/img/FpyxH41Y6_ROoePAilPNEhXnzO8=/0x0/filters:format(jpeg)/pic3490053.jpg',
            link = 'https://drive.google.com/file/d/1XOjc-n02L9pej9XVij_CfQuZaKWaq1ho/view?usp=drive_link'
        )
        rule2 = Rulebook(
            name = 'Pandemic Legacy: Season 1 (2015)',
            qdrant = 'pandemic_legacy_season_1',
            image = 'https://cf.geekdo-images.com/-Qer2BBPG7qGGDu6KcVDIw__original/img/PlzAH7swN1nsFxOXbfUvE3TkE5w=/0x0/filters:format(png)/pic2452831.png',
            link = 'https://drive.google.com/file/d/11vzFn7tXplAJ9AOtDWXCm2jq3v3UKrKD/view?usp=drive_link'
        )
        rule3 = Rulebook(
            name = 'Splendor (2014)',
            qdrant = 'splendor',
            image = 'https://cf.geekdo-images.com/rwOMxx4q5yuElIvo-1-OFw__original/img/Y2tUGY2nPTGd_epJYKQXPkQD8AM=/0x0/filters:format(jpeg)/pic1904079.jpg',
            link = 'https://drive.google.com/file/d/1Qyv0laqgdFFp5Qb4Ds8e0Fx5xjV6zu9c/view?usp=drive_link'
        )
        rule4 = Rulebook(
            name = 'Twilight Imperium: Fourth Edition (2017)',
            qdrant = 'twilight_imperium',
            image = 'https://cf.geekdo-images.com/_Ppn5lssO5OaildSE-FgFA__original/img/kVpZ0Maa_LeQGWxOqsYKP3N4KUY=/0x0/filters:format(jpeg)/pic3727516.jpg',
            link = 'https://drive.google.com/file/d/1ag2VVQOJ72km4OpQ-Hd497Tty2WVfTqT/view?usp=drive_link'
        )
        rule5 = Rulebook(
            name = 'Terraforming Mars (2016)',
            qdrant = 'terraforming',
            image = 'https://cf.geekdo-images.com/wg9oOLcsKvDesSUdZQ4rxw__original/img/thIqWDnH9utKuoKVEUqveDixprI=/0x0/filters:format(jpeg)/pic3536616.jpg',
            link = 'https://drive.google.com/file/d/1wu5j4potARoal3RBOvHT62NgBV1F4j6u/view?usp=drive_link'
        )
        rule6 = Rulebook(
            name = 'UNO',
            qdrant = 'uno',
            image = 'https://cf.geekdo-images.com/-DHiHBBSnvaLu0Do8CIykQ__imagepagezoom/img/YLahd-LQ4pAFDPZ7GvbDSjZYy6g=/fit-in/1200x900/filters:no_upscale():strip_icc()/pic8204165.jpg',
            link = 'https://drive.google.com/file/d/18XfM5Z10PU7-YkO-5Z1RHTnlNjY9c19l/view?usp=drive_link'
        )
        # insert user
        db.session.add(admin)
        db.session.add_all([test_collection, sec, thd, item1, item2, item3])
        db.session.add_all([test_history, test_chat1, test_chat2])
        db.session.add_all([rule1, rule2, rule3, rule4, rule5, rule6])
        db.session.commit()

    return app