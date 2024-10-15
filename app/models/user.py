from extensions import db

class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(70), unique = True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    roles = db.Column(db.String(100), nullable=False)
    collections = db.relationship('Collection', backref='user', lazy=True, cascade="all,delete")
    chats = db.relationship('ChatHistory', backref='user', lazy=True, cascade="all,delete")