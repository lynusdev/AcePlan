from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# Sign In
@auth.route("/signin", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Successfully signed in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("signin.html", user=current_user)

# Log Out
@auth.route("/logout")
@login_required
def logout():
    flash('Successfully signed out!', category='success')
    logout_user()
    return redirect(url_for('auth.login'))

# Sign Up
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        allowed_username_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        password = request.form.get('password')
        password_length = "X" * len(password)
        klasse = request.form.get('klasse')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', category='error')
        elif len(username) < 3:
            flash('Username must be atleast 3 characters long.', category='error')
        elif len(username) > 10:
            flash('Username cant be longer than 10 characters.', category='error')
        elif not set(username).issubset(set(allowed_username_characters)):
            flash('Username can only contain letters and numbers.', category='error')
        elif len(password) < 8:
            flash('Password must be atleast 8 characters long.', category='error')
        elif len(password) > 50:
            flash('Password cant be longer than 50 characters.', category='error')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='sha256'), passwordlength=password_length, klasse=klasse)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Successfully signed up!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)