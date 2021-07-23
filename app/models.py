from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

class Like(db.Model):
	__tablename__ = "likes"
	liker_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	liked_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Follow(db.Model):
	__tablename__ = "follows"
	follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	user_id = db.Column(db.String(8), nullable=False)

	email = db.Column(db.String(100), nullable=False)
	username = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(10), nullable=False)
	profile_picture = db.Column(db.String(10), nullable=True,\
		default="default.jpg")
	gender = db.Column(db.String(8), nullable=True)
	date_joined = db.Column(db.DateTime(), nullable=False,\
		default=datetime.utcnow)
	dob = db.Column(db.String(15), nullable=False)
	age = db.Column(db.Integer, nullable=False)

	posts = db.relationship("Post", backref="author", lazy=True)
	comments = db.relationship("Comment", backref="author", lazy=True)

	liked = db.relationship('Like', foreign_keys=[Like.liker_id],\
		backref=db.backref('liker', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')

	followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],\
		backref=db.backref('follower', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')
	followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],\
		backref=db.backref('followed', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')

	def __repr__(self):
		return f"Username: {self.username}, Email: {self.email},\
			UserID: {self.user_id}, Gender: {self.gender},\
			Date Joined: {self.date_joined}, DOB: {self.dob}, Age: {self.age}"

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)

	def is_following(self, user):
		return self.followed.filter_by(
			followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		return self.followers.filter_by(
			follower_id=user.id).first() is not None

	def like(self, post):
		if not self.is_liking(post):
			f = Like(liker=self, liked=post)
			db.session.add(f)

	def unlike(self, post):
		f = self.liked.filter_by(liked_id=post.id).first()
		if f:
			db.session.delete(f)

	def is_liking(self, post):
		return self.liked.filter_by(
			liked_id=post.id).first() is not None

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	post_id = db.Column(db.String(), unique=True, nullable=False)

	body= db.Column(db.Text, nullable=True)
	img = db.Column(db.String(), nullable=False, default=None)

	date_added = db.Column(db.DateTime(), nullable=False,\
		default=datetime.utcnow)
	comment_privacy = db.Column(db.String(), nullable=False, default="everyone")

	shared_data = db.Column(db.JSON(), nullable=True)
	shared = db.Column(db.Boolean(), nullable=False, default=False)

	author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	comments = db.relationship("Comment", backref="postData", lazy=True)
	likers = db.relationship('Like', foreign_keys=[Like.liked_id],\
		backref=db.backref('liked', lazy='joined'), lazy='dynamic',\
		cascade='all, delete-orphan')
	
	def __repr__(self):
		f"PostID: {self.post_id} Body: {self.body} Date Added: {self.date_added} "

	def is_liked_by(self, user):
		return self.likers.filter_by(
			liker_id=user.id).first() is not None

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	comment_id = db.Column(db.String(), unique=True, nullable=False)
	body= db.Column(db.Text, nullable=True)
	img = db.Column(db.String(), nullable=True)
	date_added = db.Column(db.DateTime(), nullable=False,\
        default=datetime.utcnow)

	author_id = db.Column(db.Integer, db.ForeignKey('user.id'),\
        nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'),\
        nullable=False)

	def __repr__(self):
		f"Body: {self.body} \n Date Added: {self.date_added}"