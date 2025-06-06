import os
import flask
import flask_login
import sirope
import json
from views.main.main_view import main_bp
from views.auth.auth_view import auth_bp
from views.mapa.map_view import mapa_bp
from views.profile.profile_view import profile_bp
from views.conversaciones.conversaciones_view import conversaciones_bp
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
    
    # Este loader se encarga de recargar el objeto "user" en base a la user ID almacenada en la sesión, de no existir devuelve "None"
    @lmanager.user_loader
    def load_user(user_id):
        return UserEntity.find(srp, user_id)
    
    @lmanager.unauthorized_handler
    def unauthorized_handler():
        flask.flash("Unauthorized")
        return flask.redirect("/")

# Registramos los blueprints creados en Flask.
    fapp.register_blueprint(main_bp)
    fapp.register_blueprint(auth_bp)
    fapp.register_blueprint(mapa_bp)
    fapp.register_blueprint(profile_bp)
    fapp.register_blueprint(conversaciones_bp)

    return fapp, lmanager, srp

app, lm, srp = create_app()

# Inyecta safe_oid en todas las plantillas que se carguen de flask, de esta manera se podrá acceder al perfil desde cualquier página, sin revelar nada del backend.
@app.context_processor
def inject_user_url():
    if flask_login.current_user.is_authenticated:
        try:
            safe_oid = flask_login.current_user.get_safe_oid(srp)
            return {'safe_oid': safe_oid}
        except Exception as e:
            print("Error al generar safe_oid:", e)
            return {}
    return {}

if __name__ == "__main__":
    app.run(debug=True)


