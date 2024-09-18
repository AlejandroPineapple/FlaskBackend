from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import mongo, init_db
from config import Config
from bson import ObjectId
from flask_bcrypt import Bcrypt
from Routes.auth_routes import auth_bp
from Routes.user_routes import user_bp

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
init_db(app)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    app.run(debug=True)