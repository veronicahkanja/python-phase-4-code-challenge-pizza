#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)



class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [
            restaurant.to_dict(only=('id', 'name', 'address'))
            for restaurant in restaurants
        ], 200

api.add_resource(RestaurantList, '/restaurants')



class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        return restaurant.to_dict(
            only=('id', 'name', 'address', 'restaurant_pizzas')
        ), 200

api.add_resource(RestaurantByID, '/restaurants/<int:id>')


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)

class RestaurantDelete(Resource):
    def delete(self, id):
        restaurant = Restaurant.query.get(id)

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()

        return "", 204


api.add_resource(RestaurantDelete, "/restaurants/<int:id>")

# --- Pizzas Endpoints ---

class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [
            pizza.to_dict(only=('id', 'name', 'ingredients'))
            for pizza in pizzas
        ], 200

api.add_resource(PizzaList, '/pizzas')


class PizzaByID(Resource):
    def get(self, id):
        pizza = Pizza.query.get(id)
        if not pizza:
            return {"error": "Pizza not found"}, 404
        return pizza.to_dict(), 200

api.add_resource(PizzaByID, '/pizzas/<int:id>')

class PizzaDelete(Resource):
    def delete(self, id):
        pizza = Pizza.query.get(id)
        if not pizza:
            return {"error": "Pizza not found"}, 404
        db.session.delete(pizza)
        db.session.commit()
        return "", 204

api.add_resource(PizzaDelete, '/pizzas/<int:id>')

class RestaurantPizzaCreate(Resource):
    def post(self):
        data = request.get_json()

        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        # Validate required fields
        if not price or not pizza_id or not restaurant_id:
            return {"errors": ["validation errors"]}, 400

        # Validate price range (1-30)
        if price < 1 or price > 30:
            return {"errors": ["validation errors"]}, 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return {"errors": ["validation errors"]}, 400

        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        return restaurant_pizza.to_dict(), 201


api.add_resource(RestaurantPizzaCreate, "/restaurant_pizzas")