from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////root/ncbSprint/test_api/event.db'


db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	public_id = db.Column(db.String(50), unique=True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(80))
	admin = db.Column(db.Boolean)

class Event(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(50), nullable=False)
	event_date = db.Column(db.DateTime, nullable=False)
	description = db.Column(db.String(300), nullable = False)
	creator = db.Column(db.Integer, db.ForeignKey('user.id'))

def __init__(self, public_id, name, password, admin):
	self.public_id= public_id
	self.name = name
	self.password = password
	self.admin = admin


db.create_all()
if __name__ == "__main__":
	app.run(debug = True, port=5000)