from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from models import mongo, init_db
from config import Config
from bson import ObjectId
from flask_bcrypt import Bcrypt

user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt()
jwt = JWTManager()

@user_bp.route('/', methods=['GET'])
def get_users():
    
    usuarios = mongo.db.usuarios.find({}, {})

    # Convertir el cursor de MongoDB a una lista
    lista_usuarios = []
    for usuario in usuarios:
        usuario['_id'] = str(usuario['_id'])
        usuario['preguntas_vistas'] = str(usuario['preguntas_vistas'])
        lista_usuarios.append(usuario)

    if lista_usuarios:
        return jsonify(lista_usuarios), 200
    else:
        return jsonify({"message": "No hay nadie estupido"}), 404

@user_bp.route('/', methods=['DELETE'])
def delete_user():

    data = request.get_json()
    email = data.get('email')

    if mongo.db.usuarios.find_one({"email": email}):
        mongo.db.usuarios.delete_one({"email": email})
        return jsonify({"message": "Usuario eliminado"}), 200
    else:
        return jsonify({"message": "Usuario no encontrado"}), 404

@user_bp.route('/datos', methods=['GET'])
@jwt_required()
def get_user_data():
    current_user = get_jwt_identity()
    usuario = mongo.db.usuarios.find_one({"_id": ObjectId(current_user)})
    password = usuario.get("password")

    if usuario is None:
        return jsonify({"message": "Medio esquizo de tu parte, el usuario no existe"}), 404

    if bcrypt.check_password_hash(usuario['password'], password):
        return jsonify({
            "username": usuario.get("username"),
            "email": usuario.get("email")
        }), 200
    else:
        return jsonify({"message": "Tas mal papi, el email o la contraseña son incorrectos"}), 401
    