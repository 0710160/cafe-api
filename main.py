from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Loop through each column in the database
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random():
    cafe_count = Cafe.query.count()
    random_cafe = Cafe.query.get(randint(1, cafe_count))
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def all_cafes():
    all_cafes_list = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes_list])


@app.route("/search")
def search():
    location = request.args.get("loc")
    resulting_cafes = db.session.query(Cafe).filter_by(location=location).all()
    if resulting_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in resulting_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"})


@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        seats=request.form["seats"],
        has_toilet=bool(request.form["has_toilet"]),
        has_wifi=bool(request.form["has_wifi"]),
        has_sockets=bool(request.form["has_sockets"]),
        can_take_calls=bool(request.form["can_take_calls"]),
        coffee_price=request.form["coffee_price"])
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"Success": f"Successfully added the {new_cafe.name} cafe."})


@app.route("/update_price/<cafe_id>", methods=["PATCH"])
def new_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated the coffee price."}), 200
    else:
        return jsonify(response={"Not Found": "No cafe with that ID was found in the database."}), 404


@app.route("/report_closed/<cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": "Removed closed cafe."}), 200
        else:
            return jsonify(response={"Not Found": "No cafe with that ID was found in the database."}), 404
    else:
        return jsonify(response={"Error": "Sorry, that API key is invalid."}), 403


## HTTP GET - Read Record: this is the default for an @app.route so doesn't need to be defined explicitly

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
