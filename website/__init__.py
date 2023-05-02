from flask import Flask
# from . import tv_crawler

# This file becomes a python package
# create, init, and return a flask application
def create_app():
    app = Flask(__name__)
    # encrypt cookie
    app.config['SECRET_KEY'] = 'someRandomStringIsFineForSecretKey'

    # tell flask the location of our views blueprint
    from .views import views
    # register for flask app
    app.register_blueprint(views, url_prefix='/')

    return app
