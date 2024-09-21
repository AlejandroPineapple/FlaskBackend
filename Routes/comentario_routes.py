from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import mongo, init_db
from bson.objectid import ObjectId

comentarios_bp = Blueprint('comentarios_bp', __name__)

@comentarios_bp.route('/<pregunta_id>', methods = ['POST'])
@jwt_required()
def crear_comentario(pregunta_id):

    data = request.get_json()
    texto = data.get('texto')
    
    current_user = get_jwt_identity()
    user = mongo.db.usuarios.find_one({"_id": ObjectId(current_user)})

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    username = user.get("username")

    result = mongo.db.comentarios.insert_one({"texto": texto, "username": username, "pregunta": pregunta_id})

    if result.acknowledged:
        return jsonify({"message": "Todo chido, el comentario se creo"}), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother, no se guardaron los datos"}), 400
    
@comentarios_bp.route('/<pregunta_id>', methods = ['GET'])
def mostrar_comentario(pregunta_id):
    
    comentarios = mongo.db.comentarios.find({"pregunta": pregunta_id},{"_id": 0})

    lista_comentarios = list(comentarios)

    if lista_comentarios:
        return jsonify(lista_comentarios), 200
    else:
        return jsonify({"message": "No hay nada estupido"}), 404
    
@comentarios_bp.route('/<comentario_id>', methods = ['DELETE'])
@jwt_required()
def eliminar_comentario(comentario_id):
    
    try:
        current_user = get_jwt_identity()
        user = mongo.db.usuarios.find_one({"_id": ObjectId(current_user)})
        username = user.get("username")

        if (username == "pinaman"):
            comentario = mongo.db.comentarios.find_one_and_delete({"_id": ObjectId(comentario_id)},{})
        else:
            return jsonify({"message": "No eres suficientemente chido para borrar un comentario"})

        if(not comentario):
            return jsonify({"message": "Ni borrar un comentario puedes, no se encontro"}), 400
        
        return jsonify({"message": "Ya borre tu comentario, te deberia dar verguenza"}), 200
        
    except Exception as error:
        return jsonify({"message": "Ni borrar un comentario puedes, hay un error","error": str(error)}), 400