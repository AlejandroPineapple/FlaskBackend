from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import mongo, init_db
from config import Config
from bson import ObjectId
from flask_bcrypt import Bcrypt
from datetime import timedelta


bcrypt = Bcrypt()
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if (mongo.db.usuarios.find_one({"username": username})):
        return jsonify({"message": "Ese usuario ya existe bro, que poco original"}), 400
        
    if (mongo.db.usuarios.find_one({"email": email})):
        return jsonify({"message": "Ese usuario ya existe bro, que poco original"}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    result = mongo.db.usuarios.insert_one({"username": username, "email": email, "password": hashed_password})

    if result.acknowledged:
        return jsonify({"message": "Todo chido, el usuario se creo"}), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother, no se guardaron los datos"}), 400

@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    password = data.get('password')
    email = data.get('email').lower().strip()  
    usuario = mongo.db.usuarios.find_one({"email": email})

    if usuario is None:
        return jsonify({"message": "Medio esquizo de tu parte, el usuario no existe"}), 404

    if bcrypt.check_password_hash(usuario['password'], password):
        access_token = create_access_token(identity=str(usuario["_id"]),expires_delta=timedelta(days=5000))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Tas mal papi, el email o la contraseña son incorrectos"}), 401