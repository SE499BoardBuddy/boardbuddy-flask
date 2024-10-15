import os
from dotenv import load_dotenv
load_dotenv(override=True)

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://'+os.environ.get('MYSQL_USERNAME')+':'+os.environ.get('MYSQL_PASSWORD')+'@'+os.environ.get('MYSQL_URL')+'/boardbuddy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    pass

configs = {
    'dev' : DevConfig,
    'default' : ProdConfig
}