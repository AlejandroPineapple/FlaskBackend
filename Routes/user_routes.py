from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import mongo, init_db
from flask_bcrypt import Bcrypt

user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt(__name__)
jwt = JWTManager(__name__)

@user_bp.route('/usuarios', methods=['GET'])
def get_users():
    
    usuarios = mongo.db.usuarios.find({}, {"_id": 0, "username": 1, "email": 1})

    # Convertir el cursor de MongoDB a una lista
    lista_usuarios = list(usuarios)

    if lista_usuarios:
        return jsonify(lista_usuarios), 200
    else:
        return jsonify({"message": "No hay nadie estupido"}), 404

@user_bp.route('/usuarios', methods=['DELETE'])
def delete_user():

    data = request.get_json()
    email = data.get('email')

    if mongo.db.usuarios.find_one({"email": email}):
        mongo.db.usuarios.delete_one({"email": email})
        return jsonify({"message": "Usuario eliminado"}), 200
    else:
        return jsonify({"message": "Usuario no encontrado"}), 404

@user_bp.route('/datos', methods=['POST'])
@jwt_required()
def get_user_data():
    data = request.get_json()
    password = data.get('password')
    email = data.get('email').lower().strip()  
    usuario = mongo.db.usuarios.find_one({"email": email})

    if usuario is None:
        return jsonify({"message": "Medio esquizo de tu parte, el usuario no existe"}), 404

    if bcrypt.check_password_hash(usuario['password'], password):
        access_token = create_access_token(identity=str(usuario["_id"]))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Tas mal papi, el email o la contraseña son incorrectos"}), 401
    