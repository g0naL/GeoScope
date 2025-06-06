import flask
import redis
import sirope

from model.MapEntity import Mapa
from model.ConflictEntity import Conflicto

mapa_bp = flask.Blueprint("mapa", __name__, template_folder="templates", static_folder="static", static_url_path="/mapa/static")

@mapa_bp.route("/mapa", methods=["GET", "POST"])
def mostrar_mapa():
    try:
        srp = sirope.Sirope()
        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")

        if mapa is None:
            mapa = Mapa("world_map")
            mapa.añadir_conflicto(Conflicto("ukr_ru", "Guerra en Ucrania", ["Ukraine", "Russia"], "#0057b7", "#ffd700"), srp)
            mapa.añadir_conflicto(Conflicto("in_pk", "Conflicto India - Pakistán", ["India", "Pakistan"], "#800000", "#ff9999"), srp)
            mapa.añadir_conflicto(Conflicto("ml", "Conflicto en Mali", ["Mali"], "#4B0082", "#9370DB"), srp)
            mapa.añadir_conflicto(Conflicto("sd", "Guerra en Sudán", ["Sudan"], "#8B0000", "#FFA07A"), srp)
            mapa.añadir_conflicto(Conflicto("syr", "Conflicto en Siria", ["Syria"], "#2ca02c", "#a1d99b"), srp)
            mapa.añadir_conflicto(Conflicto("ps", "Conflicto en Gaza / Palestina", ["Israel", "Palestine"], "#1f77b4", "#aec7e8"), srp)
            mapa.añadir_conflicto(Conflicto("col_vnz", "Escaramuzas entre Colombia y Venezuela", ["Colombia", "Venezuela"], "#9bb41f", "#c0aee8"), srp)
            srp.save(mapa)

        if flask.request.method == "POST":
            data = flask.request.get_json()
            conflicto_id = data.get("conflicto_id")
            marcador = {
                "lat": data.get("lat"),
                "lng": data.get("lng"),
                "texto": data.get("texto"),
                "icono": data.get("icono")
            }

            for oid in mapa.conflicto_oids:
                conflicto = srp.load(oid)
                if conflicto.id == conflicto_id:
                    conflicto.añadir_marcador(marcador)
                    srp.save(conflicto)
                    break

            return flask.jsonify(ok=True)

        conflictos = mapa.get_conflictos(srp)
        conflictos_dict = [c.to_dict() for c in conflictos]
        marcadores = {c.id: c.get_marcadores() for c in conflictos}

        return flask.render_template("mapa.html", conflictos=conflictos_dict, marcadores=marcadores)

    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos", "danger")
        return flask.redirect(flask.url_for("main.index"))

    except Exception as e:
        flask.flash(f"Error al cargar el mapa: {str(e)}", "danger")
        return flask.redirect(flask.url_for("main.index"))
