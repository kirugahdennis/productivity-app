from flask import request, session
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from server.extensions import db
from server.models.user import User
from server.schemas import signup_schema, login_schema
from server.helpers import login_required, current_user


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        try:
            valid = signup_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        user = User(username=valid["username"])
        try:
            user.password_hash = valid["password"]
        except ValueError as err:
            return {"errors": [str(err)]}, 422

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username is already taken"]}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        try:
            valid = login_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        user = User.query.filter_by(username=valid["username"]).first()

        if user and user.authenticate(valid["password"]):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"errors": ["Invalid username or password"]}, 401


class Logout(Resource):
    @login_required
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user = current_user()
        if user:
            return user.to_dict(), 200
        return {"errors": ["Not logged in"]}, 401