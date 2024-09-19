from random import randint
from flask import Flask, Blueprint, request, jsonify
from models import mongo, init_db

preguntas_bp = Blueprint('preguntas_bp', __name__)

@preguntas_bp.route('/preguntas', methods = ['POST'])
def crear_pregunta():

    data = request.get_json()
    pregunta = data.get('pregunta')
    opcion1 = data.get('opcion1')
    opcion2 = data.get('opcion2')
    print(mongo.db.preguntas.count_documents({}))
    num = (mongo.db.preguntas.count_documents({}) + 1)

    result = mongo.db.preguntas.insert_one({"pregunta": pregunta, "opcion1": opcion1, "opcion2": opcion2, "num":num})

    if result.acknowledged:
        return jsonify({"message": "Todo chido, la pregunta se creo"}), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother, no se guardaron los datos"}), 400
    
@preguntas_bp.route('/lista_preguntas', methods = ['GET'])
def mostrar_lista_preguntas():

    preguntas = mongo.db.preguntas.find({}, {"_id": 0})

    lista_preguntas = list(preguntas)

    if lista_preguntas:
        return jsonify(lista_preguntas), 200
    else:
        return jsonify({"message": "No hay nada estupido"}), 404
    
@preguntas_bp.route('/preguntas', methods = ['GET'])
def mostrar_pregunta():
    
    random_num = randint(1, mongo.db.preguntas.count_documents({})) 

    pregunta = mongo.db.preguntas.find_one({"num":random_num},{"_id": 0})

    if (pregunta):
        return jsonify(pregunta), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother"}), 400