from app import app, db
from app.models import User, Post, Comment
from flask_login import current_user
from flask import (render_template, request, redirect, url_for, abort, jsonify)
import secrets
from PIL import Image
import os

def save_picture(form_picture):
	new_name = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = new_name + f_ext
	picture_path = os.path.join(app.root_path, 'static/img/posts', picture_fn)
	i = Image.open(form_picture)
	#im = i.resize((round(i.size[0]*1), round(i.size[1]*1)))
	i.save(picture_path)
	return picture_fn

def process_image(string_array):
	string_array = string_array[1:-1]
	string_array = string_array.replace(' ', '')
	string_array = string_array.replace("'",'')

	return string_array.split(",")

@app.route('/')
def home():
	if current_user.is_authenticated:
		posts = Post.query.order_by(Post.date_added.desc()).all()
		return render_template('index.html', posts=posts,\
			process_image=process_image, len=len, enumerate=enumerate)
	else:
		return redirect(url_for('login'))

@app.route("/post/<post_id>/")
def single_post(post_id):
	if current_user.is_authenticated:
		post = Post.query.filter_by(post_id=post_id).first()
		if post:
			return render_template("single_post.html", post=post,\
				process_image=process_image, len=len, enumerate=enumerate)
		else:
			abort(404)
	else:
		return redirect(url_for('login'))

@app.route("/post/add/", methods=["POST"])
def add_post():
	if current_user.is_authenticated:
		data = request.form
		if data["shared"] == 'false':
			user = User.query.filter_by(user_id=current_user.user_id).first()
			if request.files:
				images = []
				post_img = request.files.getlist('files')
				for image in post_img:
					picture_name = save_picture(image)
					images.append(picture_name)
			else:
				images=None

			post = Post(post_id=secrets.token_hex(4),\
				body=data["text"], author=user,\
				img=str(images))
			db.session.add(post)
			db.session.commit()
		else:
			print("shared post")

		return jsonify({"message":"success"})
	else:
		abort(401)

@app.route("/post/like/", methods=["POST"])
def like_post():
	if current_user.is_authenticated:
		data = request.form
		post = Post.query.filter_by(post_id=data["post_id"]).first()
		if post:
			current_user.like(post)
			db.session.commit()
			return jsonify({"message":"liked"})
		abort(404)
	else:
		abort(401)

@app.route("/post/unlike/", methods=["POST"])
def unlike_post():
	if current_user.is_authenticated:
		data = request.form
		post = Post.query.filter_by(post_id=data["post_id"]).first()
		if post:
			current_user.unlike(post)
			db.session.commit()
			return jsonify({"message":"unliked"})
		abort(404)
	else:
		abort(401)

@app.route("/comment/add/", methods=["POST"])
def add_comment():
	if current_user.is_authenticated:
		data = request.form
		post = Post.query.filter_by(post_id=data["post_id"]).first()
		if post:
			user = User.query.filter_by(user_id=current_user.user_id).first()
			comment = Comment(comment_id=secrets.token_hex(4),\
				body=data["body"], postData=post, author=user)
			db.session.add(comment)
			db.session.commit()
			return jsonify({"message":"success"})
		abort(404)


@app.route("/profile/<user_id>/")
def profile(user_id):
	if current_user.is_authenticated:
		if current_user.user_id == user_id:
			posts = Post.query.filter_by(author=current_user).order_by(Post.date_added.desc()).all()
			return render_template("active_profile.html", posts=posts,\
				process_image=process_image, enumerate=enumerate)
		user = User.query.filter_by(user_id=user_id).first()
		if user:
			posts = Post.query.filter_by(author=user).order_by(Post.date_added.desc()).all()
			return render_template("user_profile.html", posts=posts,\
				active_user=user, process_image=process_image, enumerate=enumerate)
		abort(404)
	else:
		return redirect(url_for('login'))