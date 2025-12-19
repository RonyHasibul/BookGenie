from flask import Flask, render_template, request, redirect, url_for, flash
import numpy as np
import joblib
import pymysql
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Setup MySQL Driver for XAMPP
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'book_genie_super_secret_key'

# 1. DATABASE CONFIGURATION (XAMPP/MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/book_genie'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. DATABASE MODELS (Fulfilling SRS 3.1.5, 3.1.7, 3.1.10)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    bookmarks = db.relationship('Bookmark', backref='owner', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_title = db.Column(db.String(255), nullable=False)

class Bookmark(db.Model): # SRS 3.1.10
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_title = db.Column(db.String(255), nullable=False)

class Feedback(db.Model): # SRS 3.1.7
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_titles = db.Column(db.Text, nullable=False) 
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

# 3. LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 4. LOAD ML MODELS
popular_df = joblib.load(open('popular.pkl', 'rb'))
pt = joblib.load(open('pt.pkl', 'rb'))
books = joblib.load(open('books.pkl', 'rb'))
similarity_scores = joblib.load(open('similarity_scores.pkl', 'rb'))

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('signup'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Simulated Email Confirmation (SRS 3.1.8)
        print(f"DEBUG: Confirmation email sent to {username}@genie.com") 
        flash('Signup successful! A confirmation email has been simulated. Please login.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid Username or Password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input').strip().lower()
    # Support for Filtering by Rating (SRS 3.1.11)
    min_rating = float(request.form.get('min_rating', 0)) 

    matches = [i for i, title in enumerate(pt.index) if user_input in title.lower()]
    
    if not matches:
        return render_template('recommend.html', error="Book not found!")

    index = matches[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:15]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        
        # Apply Search Filter (SRS 3.1.11)
        if temp_df['avg_rating'].values[0] >= min_rating:
            item = temp_df.values.tolist()[0]
            data.append(item)
            
    return render_template('recommend.html', data=data[:5]) # Show top 5 filtered

# --- USER PROFILE ROUTE (SRS 3.1.5) ---

@app.route('/profile')
@login_required
def profile():
    # Fetch orders and bookmarks for the profile page
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    user_bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', orders=user_orders, bookmarks=user_bookmarks)

# --- CART, BOOKMARK & FEEDBACK ROUTES ---

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    title = request.form.get('book_title')
    db.session.add(Cart(user_id=current_user.id, book_title=title))
    db.session.commit()
    flash(f'"{title}" added to cart!')
    return redirect(request.referrer)

@app.route('/add_bookmark', methods=['POST']) # SRS 3.1.10
@login_required
def add_bookmark():
    title = request.form.get('book_title')
    existing = Bookmark.query.filter_by(user_id=current_user.id, book_title=title).first()
    if not existing:
        db.session.add(Bookmark(user_id=current_user.id, book_title=title))
        db.session.commit()
        flash(f'"{title}" added to your bookmarks!')
    else:
        flash('Already bookmarked!')
    return redirect(request.referrer)

@app.route('/contact', methods=['GET', 'POST']) # SRS 3.1.7
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        db.session.add(Feedback(name=name, email=email, message=message))
        db.session.commit()
        flash('Thank you for your feedback! Our support team will review it.')
        return redirect(url_for('index'))
    return render_template('contact.html')

@app.route('/cart')
@login_required
def cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', items=items)

@app.route('/buy_now', methods=['POST'])
@login_required
def buy_now():
    title = request.form.get('book_title')
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.add(Cart(user_id=current_user.id, book_title=title))
    db.session.commit()
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = Cart.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Cart is empty!')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        all_titles = ", ".join([i.book_title for i in items])
        new_order = Order(
            user_id=current_user.id,
            book_titles=all_titles,
            full_name=request.form.get('name'),
            address=request.form.get('address'),
            phone=request.form.get('phone')
        )
        db.session.add(new_order)
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return render_template('success.html', name=new_order.full_name)

    return render_template('checkout.html', items=items)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)