from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

# Database Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)

@app.route('/')
def index():
    return 'Welcome to my Index Page!'

@app.route('/api/products/add', methods=['POST'])
def add_product():
    data = request.json()

if __name__ == '__main__':
    app.run(debug=True)