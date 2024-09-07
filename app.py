from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import mongo, init_db
from config import Config
from bson import ObjectId
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
init_db(app)

#definir el endpoint para register
@app.route('/register', methods=['POST'])
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

    print("puto")

    if result.acknowledged:
        return jsonify({"message": "Todo chido, el usuario se creo"}), 201
    else:
        return jsonify({"message": "Algo hiciste mal brother, no se guardaron los datos"}), 400
    
@app.route('/usuarios', methods=['GET'])
def usuarios():

    # Obtener todos los usuarios de la base de datos
    usuarios = mongo.db.usuarios.find({}, {"_id": 0, "username": 1, "email": 1})

    # Convertir el cursor de MongoDB a una lista
    lista_usuarios = list(usuarios)

    if lista_usuarios:
        return jsonify(lista_usuarios), 200
    else:
        return jsonify({"message": "No hay nadie estupido"}), 404
    
@app.route('/usuarios', methods=['DELETE'])
def delete_usuario():

    data = request.get_json()
    email = data.get('email')

    if (mongo.db.usuarios.find_one({"email": email})):
        mongo.db.usuarios.delete_one({"email": email})
        return jsonify({"message": "Ya lo mataste, felicidades"}), 200
    else:
        return jsonify({"message": "Ni existe ese usuario bro"}), 404

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    password = data.get('password')
    email = data.get('email').lower().strip()  # Convertimos el email a minúsculas y quitamos espacios en blanco

    usuario = mongo.db.usuarios.find_one({"email": email})

    if usuario is None:
        return jsonify({"message": "Medio esquizo de tu parte, el usuario no existe"}), 404

    if bcrypt.check_password_hash(usuario['password'], password):
        access_token = create_access_token(identity=str(usuario["_id"]))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Tas mal papi, el email o la contraseña son incorrectos"}), 401

@app.route('/datos', methods=['POST'])
@jwt_required()
def datos():

    data = request.get_json()
    username = data.get('username')

    usuario = mongo.db.usuarios.find_one({"username": username})

    if usuario:
        usuario['_id'] = str(usuario['_id']) 
        return jsonify({"message": "Usuario encontrado, a huevoo", "Ususario": usuario}), 200
    else:
         return jsonify({"message": "Medio esquizo de tu parte, el usuario no existe"}), 404

if (__name__ == '__main__'):
    app.run(debug=True)