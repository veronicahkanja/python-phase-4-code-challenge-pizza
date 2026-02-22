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
