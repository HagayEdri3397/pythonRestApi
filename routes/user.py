from const_params.const import HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND, HTTP_OK, HTTP_UNAUTHORIZED
from database import db
from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from models import User
user_page = Blueprint('user_page', __name__, template_folder='routes/user')
jwt = JWTManager()
bcrypt = Bcrypt()

@user_page.route('/api/register', methods=['POST'])
def register_user():

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), HTTP_BAD_REQUEST

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({"message": "Username already exists"}), HTTP_BAD_REQUEST

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), HTTP_CREATED

@user_page.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), HTTP_BAD_REQUEST

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), HTTP_UNAUTHORIZED

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), HTTP_OK