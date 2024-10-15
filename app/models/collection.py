from extensions import db

class Collection(db.Model):
    __tablename__ = "collection"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), nullable=False)
    boardgames = db.relationship('CollectionItem', backref='collection', lazy=True, cascade="all,delete")
