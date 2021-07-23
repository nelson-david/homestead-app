from app import app, db, bcrypt
from app.models import User
from flask import (render_template, request, jsonify, redirect, url_for)
from flask_login import login_user, current_user, logout_user
import secrets
from datetime import datetime

@app.route("/signin/", methods=["POST", "GET"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	if request.method == "POST":
		data = request.form
		user = User.query.filter_by(username=data["username"]).first()
		if user and bcrypt.check_password_hash(user.password, data["password"]):
			login_user(user, remember=True)
			return ({'message':'success'})
		return ({'message':'failed'})
	return render_template("signin.html")

@app.route('/signup/', methods=["POST", "GET"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	if request.method == "POST":
		data = request.form
		user = User.query.filter_by(email=data["email"]).first()
		if user:
			return jsonify({'message':'exists'})
		age  = int(datetime.now().year) - int(str(data["dob"])[0:4])
		print("AGE: ", age)
		if age < 18:
			return jsonify({'message':'age_error'})

		user = User(user_id=secrets.token_hex(4), email=data["email"],\
			username=data["username"], age=age, dob=data["dob"],\
			password=bcrypt.generate_password_hash(data["password"], 8))
		db.session.add(user)
		db.session.commit()
		return jsonify({'message':'success'})
	return render_template('signup.html')