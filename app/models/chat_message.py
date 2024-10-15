from extensions import db

class ChatMessage(db.Model):
    __tablename__ = "message"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    chat_id = db.Column(db.String(50), db.ForeignKey('history.public_id'), nullable=False)
    is_human = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text, nullable=False)
