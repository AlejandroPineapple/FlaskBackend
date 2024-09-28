from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import mongo, init_db
from config import Config
from bson import ObjectId
from flask_bcrypt import Bcrypt
from Routes.auth_routes import auth_bp
from Routes.user_routes import user_bp
from Routes.pregunta_routes import preguntas_bp
from Routes.comentario_routes import comentarios_bp
#from Routes.compuertas_routes import compuertas_bp

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
init_db(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(preguntas_bp, url_prefix='/preguntas')
app.register_blueprint(comentarios_bp, url_prefix='/comentarios')
#app.register_blueprint(compuertas_bp, url_prefix='/compuertas')

if __name__ == '__main__':
    app.run(debug=True)