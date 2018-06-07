from flask import Flask, redirect, url_for, render_template, request

from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()


app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass'
app.config['MYSQL_DATABASE_DB'] = 'bank'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def home():
	return redirect(url_for("login"))

@app.route("/success/<uname>")
def success(uname):
	return "Welcome {}".format(uname)

@app.route("/failure/<uname>")
def failure(uname):
	return "Incorrect username or password for user: {}".format(uname)

@app.route("/empty")
def empty():
	return 'At least one field is empty'

@app.route("/hello/<user>")
def hello_msg(user):
	return "Hello World, {} is learning flask for the first time ever!!".format(user)

@app.route("/login", methods=["get", "post"])
def login():

	if request.method == "POST":
		username = request.form['uname']
		password = request.form['pwd']

		#if (not username) or (not password):
		#	return redirect(url_for('empty'))

		conn = mysql.connect()
		cursor = conn.cursor()

		try: 
			query= 'select * from user where user='"+username+"' and password=md5('"+password+"');'
			#print(query)
			cursor.execute(query)
			data = cursor.fetchall()
			for row in rows:
				print(row)
			if data is None:
				return redirect(url_for('failure', name=username))
			else:
				return redirect(url_for("success", uname=username))


		except Exception as e:
			print(e)
		finally:
			conn.close()
		return render_template('loans.html', data=rows)	

	#	if username == "admin" and password == "password":
	#		return redirect(url_for("success", uname=username))
	#	else:
	#		return redirect(url_for("failure", uname=username))

	return render_template("login.html")



if __name__ == "__main__":
	app.run(debug = True, port=8080)