from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////root/ncbSprint/test_api/event.db'
app.config['SECRET_KEY'] = 'muthgu3jf4u3hgi3o4jg9'


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

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		if not token:
			return jsonify({'Message':'Token is unavailable'})
		try:
			data = jwt.decode(token,app.config['SECRET_KEY'])
			current_user = User.query.filter_by(public_id=data['public_id']).first()
		except:
			return jsonify({'Message':'Token invalid!'}), 401
		return f(current_user, *args, **kwargs)
	return decorated





@app.route('/user', methods=["POST"])
@token_required
def create_user(current_user):

	if not current_user.admin:
		return jsonify({'Message':'Cannot perform this function'})

	data = request.get_json()
	hashed_password = generate_password_hash(data['password'], method= 'sha256')
	new_user = User(public_id = str(uuid.uuid4()),name = data['name'], password=hashed_password, admin=False)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'Message':'User created'})

@app.route('/admin', methods=["POST"])
@token_required
def create_admin(current_user):
	data = request.get_json()
	hashed_password = generate_password_hash(data['password'], method= 'sha256')
	new_user = User(public_id = str(uuid.uuid4()),name = data['name'], password=hashed_password, admin=True)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'Message':'User created'})

@app.route('/user', methods=['GET'])
def get_users():
	users = User.query.all()
	output = []
	for user in users:
		user_data = {}
		user_data['public_id'] = user.public_id
		user_data['name'] = user.name
		user_data['password'] = user.password
		user_data['admin'] = user.admin
		output.append(user_data)
	return jsonify({'users':output})

@app.route('/user/<public_id>', methods=['GET'])
def get_user(public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'Message':'User does not exist'})
	user_data={}
	user_data['public_id'] = user.public_id
	user_data['name'] = user.name
	user_data['password'] = user.password
	user_data['admin'] = user.admin
	return jsonify({'user':user_data})

#Promote/Demote Users
@app.route('/user/p/<public_id>', methods=['PUT'])
@token_required
def promote_user(public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'Message':'user does not exist'})
	user.admin = True
	db.session.commit()
	return jsonify({"Message":"User Promoted"})

@app.route('/user/d/<public_id>', methods=['PUT'])
@token_required
def demote_user(public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'Message':'user does not exist'})
	user.admin = False
	db.session.commit()
	return jsonify({"Message":"User Demoted"})

#Delete User
@app.route('/user/<public_id>',methods=['DELETE'])
@token_required
def delete_user(public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'Message':'user does not exist'})
	db.session.delete(user)
	db.session.commit()
	return jsonify({"Message":"User Deleted"})

@app.route('/login')
def login():
	auth = request.authorization
	if not auth or not auth.username or not auth.password:
		return make_response('Authentication not verified', 401, {'WWW-Authenticate':'Basic realm="login Required!"'})
	user = User.query.filter_by(name=auth.username).first()
	
	if not user:
		return make_response('Authentication not verified', 401, {'WWW-Authenticate':'Basic realm="login Required!"'})
	
	if check_password_hash(user.password,auth.password):
		token = jwt.encode({'public_id':user.public_id, 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
		return  jsonify({'token':token.decode('UTF-8')})

	return make_response('Authentication not verified', 401, {'WWW-Authenticate':'Basic realm="login Required!"'})

@app.route('/event',methods=['POST'])
@token_required
def create_event(current_user):
	data = request.get_json()
	new_event(title=data['title'], event_data=datetime.datetime.utcnow(), description=data['description'],creator=current_user.id)


if __name__ == "__main__":
	app.run(debug = True, port=5000)


