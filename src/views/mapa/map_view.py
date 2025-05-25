import flask
import redis
import sirope

from model.ConflictEntity import Conflicto
from model.Map import Mapa

mapa_bp = flask.Blueprint("mapa", __name__, template_folder="templates", static_folder="static", static_url_path="/mapa/static")

@mapa_bp.route("/mapa", methods=["GET"])
def mostrar_mapa():

    try:
        srp = sirope.Sirope()

        mapa_guardado = srp.find_first(Mapa, lambda m: True)

        if not mapa_guardado:
            mapa = Mapa()

            mapa.añadir_conflicto("ucrania", "Guerra en Ucrania", ["Ukraine", "Russia"], "#0057b7", "#ffd700")
            mapa.añadir_conflicto("india_pakistan", "Conflicto India - Pakistán", ["India", "Pakistan"], "#800000", "#ff9999")
            mapa.añadir_conflicto("mali", "Conflicto en Mali", ["Mali"], "#4B0082", "#9370DB")
            mapa.añadir_conflicto("sudan", "Guerra en Sudán", ["Sudan"], "#8B0000", "#FFA07A")
            mapa.añadir_conflicto("siria", "Conflicto en Siria", ["Syria"], "#2ca02c", "#a1d99b")
            mapa.añadir_conflicto("gaza", "Conflicto en Gaza / Palestina", ["Israel", "Palestine"], "#1f77b4", "#aec7e8")

            srp.save(mapa)
        else:
            mapa = mapa_guardado

        return flask.render_template("mapa.html", mapa=mapa)
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos para registrarse, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))
#    except Exception:
#       flask.flash("Ha ocurrido un problema a la hora de cargar los conflictos en el mapa, inténtelo más tarde.", "danger")
#        return flask.redirect(flask.url_for("main.index"))

