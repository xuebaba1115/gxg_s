from .wxauth import users

def register_blueprints(app):
    app.register_blueprint(users)