from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # For security purposes, in production use a secure, environment-specific key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Service Provider Model
class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(200))
    service_type = db.Column(db.String(50), nullable=False)
    service_description = db.Column(db.Text)
    areas_served = db.Column(db.String(200))
    availability = db.Column(db.String(100))
    pricing_info = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    reviews = db.relationship('Review', backref='provider', lazy=True)

# Review Model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    reviewer = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('provider', 'Service Provider')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # In production, use secure password hashing
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template_string(open('login.html').read(), form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template_string(open('register.html').read(), form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'provider':
        return render_template_string(open('provider_dashboard.html').read())
    else:
        return render_template_string(open('customer_dashboard.html').read())

@app.route('/service_providers', methods=['GET'])
def get_providers():
    providers = ServiceProvider.query.all()
    output = []
    for provider in providers:
        provider_data = {
            'id': provider.id,
            'name': provider.name,
            'email': provider.email,
            'phone': provider.phone,
            'website': provider.website,
            'service_type': provider.service_type,
            'service_description': provider.service_description,
            'areas_served': provider.areas_served,
            'availability': provider.availability,
            'pricing_info': provider.pricing_info,
            'rating': provider.rating,
            'reviews': [{'reviewer': r.reviewer, 'comment': r.comment, 'stars': r.stars} for r in provider.reviews]
        }
        output.append(provider_data)
    return jsonify({'service_providers': output})

@app.route('/service_providers', methods=['POST'])
@login_required
def create_provider():
    if current_user.role != 'provider':
        return jsonify({"message": "Unauthorized"}), 403
    data = request.json
    new_provider = ServiceProvider(
        name=data['name'], 
        email=data['email'], 
        phone=data['phone'], 
        website=data.get('website', ''), 
        service_type=data['service_type'], 
        service_description=data['service_description'],
        areas_served=data['areas_served'],
        availability=data['availability'],
        pricing_info=data.get('pricing_info', '')
    )
    db.session.add(new_provider)
    db.session.commit()
    return jsonify({"message": "Service Provider added successfully", "id": new_provider.id}), 201

@app.route('/service_providers/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    provider = ServiceProvider.query.get_or_404(provider_id)
    provider_data = {
        'id': provider.id,
        'name': provider.name,
        'email': provider.email,
        'phone': provider.phone,
        'website': provider.website,
        'service_type': provider.service_type,
        'service_description': provider.service_description,
        'areas_served': provider.areas_served,
        'availability': provider.availability,
        'pricing_info': provider.pricing_info,
        'rating': provider.rating,
        'reviews': [{'reviewer': r.reviewer, 'comment': r.comment, 'stars': r.stars} for r in provider.reviews]
    }
    return jsonify(provider_data)

@app.route('/service_providers/<int:provider_id>/reviews', methods=['POST'])
@login_required
def add_review(provider_id):
    provider = ServiceProvider.query.get_or_404(provider_id)
    data = request.json
    new_review = Review(
        provider_id=provider_id,
        reviewer=data['reviewer'],
        comment=data['comment'],
        stars=data['stars']
    )
    db.session.add(new_review)
    db.session.commit()
    
    # Update provider's rating
    total_stars = sum([review.stars for review in provider.reviews])
    provider.rating = total_stars / len(provider.reviews) if provider.reviews else 0.0
    db.session.commit()
    
    return jsonify({"message": "Review added successfully"})

@app.route('/service_providers/<int:provider_id>', methods=['PUT'])
@login_required
def update_provider(provider_id):
    if current_user.role != 'provider':
        return jsonify({"message": "Unauthorized"}), 403
    provider = ServiceProvider.query.get_or_404(provider_id)
    data = request.json
    provider.name = data.get('name', provider.name)
    provider.email = data.get('email', provider.email)
    provider.phone = data.get('phone', provider.phone)
    provider.website = data.get('website', provider.website)
    provider.service_type = data.get('service_type', provider.service_type)
    provider.service_description = data.get('service_description', provider.service_description)
    provider.areas_served = data.get('areas_served', provider.areas_served)
    provider.availability = data.get('availability', provider.availability)
    provider.pricing_info = data.get('pricing_info', provider.pricing_info)
    db.session.commit()
    return jsonify({"message": "Service Provider updated successfully"})

@app.route('/service_providers/<int:provider_id>', methods=['DELETE'])
@login_required
def delete_provider(provider_id):
    if current_user.role != 'provider':
        return jsonify({"message": "Unauthorized"}), 403
    provider = ServiceProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({"message": "Service Provider deleted successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)