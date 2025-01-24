from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app and the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'customer' or 'provider'

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Create a new user instance
        new_user = User(username=username, email=email, password=password, user_type=user_type)
        
        # Add user to the database
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to login page after successful signup
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query the user from the database
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and the password matches
        if user and user.password == password:
            return redirect(url_for('dashboard', user_type=user.user_type))
        else:
            return "Invalid email or password", 400
    
    return render_template('login.html')

# Route for the user dashboard (customer or provider)
@app.route('/dashboard/<user_type>')
def dashboard(user_type):
    if user_type == 'customer':
        return render_template('customer_dashboard.html')
    elif user_type == 'provider':
        return render_template('provider_dashboard.html')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
