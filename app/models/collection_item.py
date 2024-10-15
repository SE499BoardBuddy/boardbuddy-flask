from extensions import db

class CollectionItem(db.Model):
    __tablename__ = "item"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    bg_id = db.Column(db.Integer, nullable=False)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    collection_id = db.Column(db.String(50), db.ForeignKey('collection.public_id'), nullable=False)
    # __table_args__ = (
    #     db.PrimaryKeyConstraint(
    #         bg_id, collection_id,
    #     ),
    #     {'extend_existing': True}
    # )
