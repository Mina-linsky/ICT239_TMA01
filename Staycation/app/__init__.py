# from flask import Flask
# from flask_mongoengine import MongoEngine, Document
# from flask_login import LoginManager

# import pymongo

# def create_app():
#     app = Flask(__name__)
#     app.config['MONGODB_SETTINGS'] = {
#         'db':'staycation',
#         'host':'localhost',
#         # 'port': 27017

#     }
#     app.static_folder = 'assets'
#     db = MongoEngine(app)

#     app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
#     login_manager = LoginManager()
#     login_manager.init_app(app)
#     login_manager.login_view = 'auth.login'
#     login_manager.login_message = "Please login or register first to get an account."
#     return app, db, login_manager

# app, db, login_manager = create_app()

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

db = MongoEngine()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        'db': 'staycation',
        'host': 'localhost',
    }
    app.static_folder = 'assets'
    
    db.init_app(app)
    
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login or register first to get an account."

    # from app.models.book import Booking
    # from app.models.forms import RegForm, BookForm
    # from app.models.lib_books import Book
    # from app.models.package import Package
    # from app.models.users import User

    from app.controllers.dashboard import dashboard
    from app.controllers.auth import auth
    from app.controllers.bookController import booking
    from app.controllers.packageController import package
    
    app.register_blueprint(dashboard)
    app.register_blueprint(auth)
    app.register_blueprint(booking)
    app.register_blueprint(package)

    return app


