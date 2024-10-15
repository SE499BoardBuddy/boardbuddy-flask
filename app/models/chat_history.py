from extensions import db

class ChatHistory(db.Model):
    __tablename__ = "history"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True, nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    game = db.Column(db.Integer, nullable=False)
    chats = db.relationship('ChatMessage', backref='history', lazy=True, cascade="all,delete")
