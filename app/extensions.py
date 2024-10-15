from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch

import os
from dotenv import load_dotenv
load_dotenv(override=True)

db = SQLAlchemy()
es_client = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.environ.get('ELASTIC_KEY')),
    ca_certs="~/http_ca.crt"
)
