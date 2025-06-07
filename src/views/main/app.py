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
from model.MapEntity import Mapa
from model.ConflictEntity import Conflicto

def init_mapa(srp):

    if srp.find_first(Mapa, lambda m: m.id == "world_map") is None:
        mapa = Mapa("world_map")
        mapa.añadir_conflicto(Conflicto(
            "ukr_ru", "Guerra en Ucrania", ["Ukraine", "Russia"],
            "#0057b7", "#ffd700",
            "Conflicto armado iniciado en 2022 entre Ucrania y Rusia tras la invasión rusa del territorio ucraniano."
        ), srp)

        mapa.añadir_conflicto(Conflicto(
            "in_pk", "Conflicto India - Pakistán", ["India", "Pakistan"],
            "#800000", "#ff9999",
            "Disputa histórica centrada principalmente en la región de Cachemira, con tensiones fronterizas recurrentes."
        ), srp)

        mapa.añadir_conflicto(Conflicto(
            "ml", "Conflicto en Mali", ["Mali"],
            "#4B0082", "#9370DB",
            "Insurgencia armada en el norte de Mali entre grupos separatistas, yihadistas y el gobierno central."
        ), srp)

        mapa.añadir_conflicto(Conflicto(
            "sd", "Guerra en Sudán", ["Sudan"],
            "#8B0000", "#FFA07A",
            "Enfrentamiento entre el ejército sudanés y las Fuerzas de Apoyo Rápido desde abril de 2023."
        ), srp)

        mapa.añadir_conflicto(Conflicto(
            "syr", "Conflicto en Siria", ["Syria"],
            "#2ca02c", "#a1d99b",
            "Guerra civil iniciada en 2011 con múltiples actores locales e internacionales involucrados."
        ), srp)

        mapa.añadir_conflicto(Conflicto(
            "ps", "Conflicto en Gaza / Palestina", ["Israel", "Palestine"],
            "#1f77b4", "#aec7e8",
            "Escalada de violencia entre Israel y grupos armados palestinos, especialmente en la Franja de Gaza."
        ), srp)

        mapa.añadir_conflicto(Conflicto(
            "col_vnz", "Escaramuzas entre Colombia y Venezuela", ["Colombia", "Venezuela"],
            "#9bb41f", "#c0aee8",
            "Tensiones fronterizas entre fuerzas militares y grupos armados en zonas limítrofes de ambos países."
        ), srp)
        srp.save(mapa)

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
    def load_user(user_id):
        return UserEntity.find(srp, user_id)

    @lmanager.unauthorized_handler
    def unauthorized_handler():
        flask.flash("Unauthorized")
        return flask.redirect("/")

    # Blueprints
    fapp.register_blueprint(main_bp)
    fapp.register_blueprint(auth_bp)
    fapp.register_blueprint(mapa_bp)
    fapp.register_blueprint(profile_bp)
    fapp.register_blueprint(conversaciones_bp)

    # Crear mapa si no existe
    init_mapa(srp)

    return fapp, lmanager, srp

app, lm, srp = create_app()

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
