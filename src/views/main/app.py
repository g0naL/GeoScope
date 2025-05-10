import os
import flask
import flask_login
import sirope
import json
from views.main.main_view import main_bp
from views.auth.auth_view import auth_bp
from views.mapa.map_view import mapa_bp
from model.UserEntity import UserEntity


def create_app():
    lmanager = flask_login.LoginManager()
    fapp = flask.Flask(
        __name__,
        instance_path=os.path.join(os.path.dirname(__file__), "../../instance"),
        instance_relative_config=True
    )
    
    srp = sirope.Sirope()

    fapp.config.from_file("config.json", load=json.load)
    lmanager.init_app(fapp)
    
    @lmanager.user_loader
    def load_user(email):
        return UserEntity.find(srp, email)

# Registramos los blueprints creados en Flask.
    fapp.register_blueprint(main_bp)
    fapp.register_blueprint(auth_bp)
    fapp.register_blueprint(mapa_bp)

    return fapp, lmanager, srp

app, lm, srp = create_app()

if __name__ == "__main__":
    app.run(debug=True)

