from random import randint
from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import mongo, init_db
from bson.objectid import ObjectId

preguntas_bp = Blueprint('preguntas_bp', __name__)

@preguntas_bp.route('/', methods = ['POST'])
def crear_pregunta():

    data = request.get_json()
    pregunta = data.get('pregunta')
    opcion1 = data.get('opcion1')
    opcion2 = data.get('opcion2')
    opcion1_elegida = 0
    opcion2_elegida = 0
    oculta = False
    num = (mongo.db.preguntas.count_documents({}) + 1)
    print("Numero de preguntas actuales ", mongo.db.preguntas.count_documents({}))

    if (mongo.db.preguntas.find_one({"pregunta":pregunta}) and mongo.db.preguntas.find_one({"opcion1":opcion1}) and mongo.db.preguntas.find_one({"opcion2":opcion2})):
        return jsonify({"message": "Tantita mas originalidad, esa exacta pregunta y opciones ya existen"}), 420

    result = mongo.db.preguntas.insert_one({"pregunta": pregunta, "opcion1": opcion1, "opcion2": opcion2, "opcion1_elegida":opcion1_elegida, "opcion2_elegida":opcion2_elegida, "oculta":oculta, "num":num})

    if result.acknowledged:
        return jsonify({"message": "Todo chido, la pregunta se creo"}), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother, no se guardaron los datos"}), 400
    
@preguntas_bp.route('/lista', methods = ['GET'])
def mostrar_lista_preguntas():
    preguntas = mongo.db.preguntas.find({"oculta": False}, {})

    lista_preguntas = []
    for pregunta in preguntas:
        pregunta['_id'] = str(pregunta['_id'])
        lista_preguntas.append(pregunta)

    if lista_preguntas:
        return jsonify(lista_preguntas), 200
    else:
        return jsonify({"message": "No hay nada estupido"}), 404
    
@preguntas_bp.route('/logeado', methods = ['GET'])
@jwt_required()
def mostrar_pregunta():

    current_user = get_jwt_identity()
    user = mongo.db.usuarios.find_one({"_id": ObjectId(current_user)})

    if not user:
        return jsonify({"message": "Algo hiciste mal brother"}), 400
    
    preguntas_vistas = user.get("preguntas_vistas", [])
    
    pregunta = mongo.db.preguntas.aggregate([
    {
        "$match": {
            "_id": {"$nin": preguntas_vistas},  # Excluir preguntas vistas
            "oculta": False  # Excluir preguntas ocultas
        }
    },
    {"$sample": {"size": 1}}  # Seleccionar una pregunta al azar
    ])

    pregunta = list(pregunta)

    if not pregunta:
        random_num = randint(1, mongo.db.preguntas.count_documents({})) 
        pregunta = mongo.db.preguntas.find_one({"num":random_num},{})

        while (pregunta["oculta"] == True):
            random_num = randint(1, mongo.db.preguntas.count_documents({})) 
            pregunta = mongo.db.preguntas.find_one({"num":random_num},{})

        pregunta["_id"] = str(pregunta["_id"])

        if (pregunta):
            return jsonify(pregunta), 201
        else:
            return jsonify({"message": "Algo hiciste mal brother"}), 400
    
    pregunta = pregunta[0] 
    pregunta["_id"] = str(pregunta["_id"])

    mongo.db.usuarios.update_one(
        {"_id": ObjectId(current_user)},  
        {"$push": {"preguntas_vistas": ObjectId(pregunta["_id"])}}  
    )

    if (pregunta):
        return jsonify(pregunta), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother"}), 400

@preguntas_bp.route('/', methods = ['GET'])
def mostrar_pregunta_random():
    random_num = randint(1, mongo.db.preguntas.count_documents({})) 
    pregunta = mongo.db.preguntas.find_one({"num":random_num},{})

    while (pregunta["oculta"] == True):
        random_num = randint(1, mongo.db.preguntas.count_documents({})) 
        pregunta = mongo.db.preguntas.find_one({"num":random_num},{})

    pregunta["_id"] = str(pregunta["_id"])

    if (pregunta):
        return jsonify(pregunta), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother"}), 400

@preguntas_bp.route('/<pregunta_id>', methods = ['DELETE'])
@jwt_required()
def ocultar_pregunta(pregunta_id):

    current_user = get_jwt_identity()
    user = mongo.db.usuarios.find_one({"_id": ObjectId(current_user)})
    username = user.get("username")

    if (username == "pinaman"):
        mongo.db.preguntas.update_one(
            {"_id": ObjectId(pregunta_id)},  
            {"$set": {"oculta": True}} 
        )       
        return jsonify({"message": "Pregunta ocultada por degenerado"})
    else:
        return jsonify({"message": "No eres suficientemente chido para borrar una pregunta"})

@preguntas_bp.route('/<pregunta_id>', methods=['POST'])
def elegir_opcion(pregunta_id):

    data = request.get_json()
    opcion = data.get('opcion')

    try:
        pregunta = mongo.db.preguntas.find_one({"_id": ObjectId(pregunta_id)}, {})
    except:
        return jsonify({"message": "ID de pregunta inválido"}), 400

    if not pregunta:
        return jsonify({"message": "Pregunta no encontrada"}), 404
    
    opcion1 = pregunta.get("opcion1")
    opcion2 = pregunta.get("opcion2")

    opcion1_elegida = pregunta.get("opcion1_elegida", 0)
    opcion2_elegida = pregunta.get("opcion2_elegida", 0)

    if opcion == opcion1:
        mongo.db.preguntas.update_one(
            {"_id": ObjectId(pregunta_id)},
            {"$set": {"opcion1_elegida": opcion1_elegida + 1}}
        )
        return jsonify({"message": "Votaste por la opcion: "+ opcion  + " yupii"}), 200

    elif opcion == opcion2:
        mongo.db.preguntas.update_one(
            {"_id": ObjectId(pregunta_id)},
            {"$set": {"opcion2_elegida": opcion2_elegida + 1}}
        )
        return jsonify({"message": "Votaste por la opcion: "+ opcion + " yupii"}), 200

    else:
        return jsonify({"message": "Seria maravilloso que eligieras una opcion real"}), 400