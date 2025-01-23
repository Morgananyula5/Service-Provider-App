from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(200))  # New field for website
    service_type = db.Column(db.String(50), nullable=False)
    service_description = db.Column(db.Text)  # New field for service description
    areas_served = db.Column(db.String(200))  # New field for areas served
    availability = db.Column(db.String(100))  # New field for availability
    pricing_info = db.Column(db.Text)  # New field for pricing information
    rating = db.Column(db.Float, default=0.0)  # New field for rating
    reviews = db.relationship('Review', backref='provider', lazy=True)  # Relationship for reviews

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    reviewer = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

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
def create_provider():
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
def update_provider(provider_id):
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
def delete_provider(provider_id):
    provider = ServiceProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({"message": "Service Provider deleted successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)