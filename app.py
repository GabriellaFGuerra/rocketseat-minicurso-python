from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SECRET_KEY"] = "katara-bicho-chato"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
CORS(app)


# Database Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    cart = db.relationship("CartItem", backref="user", lazy=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return "Welcome to my Index Page!"


@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if "username" in data and "password" in data:

        user = User(
            username=data["username"],
            password=data["password"],
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Usário adicionado com sucesso"}), 201

    return jsonify({"error": "Campos obrigatórios ausentes"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if "username" in data and "password" in data:
        user = User.query.filter_by(username=data["username"]).first()

        if user and user.password == data["password"]:
            login_user(user)
            return jsonify({"message": "Login bem-sucedido"}), 200

        return jsonify({"error": "Credenciais inválidas"}), 401

    return jsonify({"error": "Campos obrigatórios ausentes"}), 400


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout bem-sucedido"}), 200


@app.route("/api/products/add", methods=["POST"])
@login_required
def add_product():
    data = request.json

    if "name" in data and "price" in data:

        product = Product(
            name=data["name"],
            price=data["price"],
            description=data.get("description", ""),
        )

        db.session.add(product)
        db.session.commit()

        return jsonify({"message": "Produto adicionado com sucesso"}), 201

    return jsonify({"error": "Campos obrigatórios ausentes"}), 400


@app.route("/api/products/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_product(id):
    product = Product.query.get(id)

    if product:
        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Produto excluído com sucesso"}), 200

    return jsonify({"error": "Produto não encontrado"}), 404


@app.route("/api/products/update/<int:id>", methods=["PUT"])
@login_required
def update_product(id):
    product = Product.query.get(id)

    if product:
        data = request.json

        if "name" in data:
            product.name = data["name"]

        if "price" in data:
            product.price = data["price"]

        if "description" in data:
            product.description = data["description"]

        db.session.commit()

        return jsonify({"message": "Produto atualizado com sucesso"}), 200

    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404


@app.route("/api/products/<int:id>", methods=["GET"])
@login_required
def get_product(id):
    product = Product.query.get(id)

    if product:
        return jsonify(
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
            }
        )

    return jsonify({"error": "Produto não encontrado"}), 404


@app.route("/api/products", methods=["GET"])
def get_all_products():
    products = Product.query.all()
    products_list = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
        }
        products_list.append(product_dict)

    return jsonify(products_list), 200


@app.route("/api/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    user = User.query.get(int(current_user.id))
    product = Product.query.get(int(product_id))

    if user and product:
        cart_item = CartItem(user=user.id, product=product.id)

        db.session.add(cart_item)
        db.session.commit()
        return jsonify({"message": "Item adicionado ao carrinho"}), 201

    return jsonify({"error": "Usário ou produto não encontrado"}), 404


@app.route("/api/cart/remove/<int:product_id>", methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
    user = User.query.get(int(current_user.id))
    product = Product.query.get(int(product_id))

    if user and product:
        cart_item = CartItem.query.filter_by(
            user=current_user.id, product=product.id
        ).first()

        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({"message": "Item removido do carrinho"}), 200

        return jsonify({"error": "Item não encontrado no carrinho"}), 404

    return jsonify({"error": "Usário ou produto nao encontrado"}), 404


@app.route("/api/cart", methods=["GET"])
@login_required
def get_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_items_list = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product)
        cart_items_list.append = {
            "id": cart_item.id,
            "name": product.name,
            "price": product.price,
        }


@app.route("/api/cart/checkout", methods=["POST"])
@login_required
def checkout():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Checkout bem-sucedido"}), 200


if __name__ == "__main__":
    app.run(debug=True)
