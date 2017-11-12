from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_marshmallow import Marshmallow
from marshmallow import fields
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'doctorsAPI.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


# A Doctor model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __init__(self, name):
        self.name = name


# A Review Model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    doctor = db.relationship("Doctor", backref=db.backref("reviews", lazy="dynamic"))

    def __init__(self, description,  doctor_id, doctor):
        self.description = description
        self.doctor_id = doctor_id
        self.doctor = doctor


# Doctor Schema
class DoctorSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    reviews = fields.Nested('ReviewSchema', many=True, exclude=("doctor", ))


# Review Schema
class ReviewSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    doctor_id = fields.Int()
    doctor = fields.Nested('DoctorSchema', only=('id', 'name'))


doctor_schema = DoctorSchema()
doctors_schema = DoctorSchema(many=True)

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)


# endpoint to create a new doctor
@app.route("/doctors", methods=["POST"])
def add_doctor():
    name = request.json['doctor']['name']
    new_doctor = Doctor(name)

    db.session.add(new_doctor)
    db.session.commit()

    s = doctor_schema.dumps(new_doctor)
    return s.data


# endpoint to show all doctors
@app.route("/doctors", methods=["GET"])
def get_doctor():
    all_doctors = Doctor.query.all()
    result = doctors_schema.dump(all_doctors)
    return jsonify({'doctors': result.data})


# endpoint to get doctor details and reviews by id
@app.route("/doctors/<int:pk>", methods=["GET"])
def doctor_detail(pk):

    doctor = Doctor.query.get(pk)

    if doctor is None:
        return jsonify("Doctor could not be found"), 400

    doctor_result = doctor_schema.dump(doctor)
    return jsonify(doctor_result.data)


# endpoint to create a new review for a doctor
@app.route("/doctors/<int:pk>/reviews", methods=["POST"])
def add_review(pk):
    description = request.json['review']['description']

    doctor = Doctor.query.filter_by(id=pk).first()
    if doctor is None:
        return jsonify("Doctor could not be found"), 400

    review_result = Review(description, pk, doctor)

    db.session.add(review_result)
    db.session.commit()
    result = review_schema.dump(Review.query.get(review_result.id))
    return jsonify(result.data)


# endpoint to get a review (by id) from a doctor (by id)
@app.route("/doctors/<int:pk>/reviews/<int:rk>", methods=["GET"])
def get_review(pk, rk):

    doctor = Doctor.query.get(pk)
    if doctor is None:
        return jsonify("Doctor could not be found"), 400

    review = Review.query.get(rk)
    if review is None:
        return jsonify("Review could not be found"), 400

    review_result = review_schema.dump(review)
    return jsonify(review_result.data)


# endpoint to delete a doctor (by id)
@app.route("/doctors/<int:pk>", methods=["DELETE"])
def delete_doctor(pk):
    doctor = Doctor.query.get(pk)

    if doctor is None:
        return jsonify("Doctor could not be found in order to delete"), 400

    db.session.delete(Doctor.query.get(pk))
    db.session.commit()
    return jsonify("Deleted doctor.")


# endpoint to delete a review of a doctor
@app.route("/doctors/<int:pk>/reviews/<int:rk>", methods=["DELETE"])
def delete_review(pk, rk):
    doctor = Doctor.query.get(pk)
    if doctor is None:
        return jsonify("Doctor could not be found in order to complete deletion"), 400

    review = Review.query.get(rk)
    if review is None:
        return jsonify("Review could not be found in order to complete deletion"), 400

    db.session.delete(Review.query.get(rk))
    db.session.commit()
    return jsonify("Deleted review.")


if __name__ == '__main__':
    app.run(debug=True)