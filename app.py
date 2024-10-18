from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import random, string

from config import Config
from models import db, User, URL, Click

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to generate a random short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login failed. Check your credentials.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls)

@app.route('/shorten', methods=['POST'])
@login_required
def shorten_url():
    original_url = request.form['original_url']
    short_url = generate_short_url()
    new_url = URL(original_url=original_url, short_url=short_url, user_id=current_user.id)
    db.session.add(new_url)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/<short_url>')
def redirect_short_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    
    # Log the click
    click = Click(ip_address=request.remote_addr, url_id=url.id)
    db.session.add(click)
    db.session.commit()

    return redirect(url.original_url)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
