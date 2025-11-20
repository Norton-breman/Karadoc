from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class FileModel(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    path = db.Column(db.String(500), nullable=False)
    artwork = db.Column(db.Text)  # Base64 encoded artwork
    parent = db.Column(db.Integer, ForeignKey('files.id'))
    url = db.Column(db.String(500))
    description = db.Column(db.Text)
    album = db.Column(db.String(50))
    artist = db.Column(db.String(50))
    name = db.Column(db.String(50))
