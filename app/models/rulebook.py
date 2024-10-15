from extensions import db

class Rulebook(db.Model):
    __tablename__ = "rulebook"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    qdrant = db.Column(db.String(50), nullable=False)
    image = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text)
