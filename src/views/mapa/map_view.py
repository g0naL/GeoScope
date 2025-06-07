import flask
import redis
import sirope

from model.MapEntity import Mapa
from model.ConflictEntity import Conflicto

mapa_bp = flask.Blueprint("mapa", __name__, template_folder="templates", static_folder="static", static_url_path="/mapa/static")

@mapa_bp.route("/mapa", methods=["GET", "POST", "DELETE"])
def mostrar_mapa():
    try:
        srp = sirope.Sirope()
        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")

        if mapa is None:
            if flask.request.method == "GET":
                flask.flash("No se encontró el mapa", "danger")
                return flask.redirect(flask.url_for("main.index"))
            else:
                return flask.jsonify(ok=False, msg="Mapa no encontrado"), 404

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
                    return flask.jsonify(ok=True)

            return flask.jsonify(ok=False, msg="Conflicto no encontrado"), 404

        if flask.request.method == "DELETE":
            data = flask.request.get_json()
            conflicto_id = data.get("conflicto_id")
            lat = data.get("lat")
            lng = data.get("lng")

            if not (conflicto_id and lat is not None and lng is not None):
                return flask.jsonify(ok=False, msg="Parámetros incompletos"), 400

            for oid in mapa.conflicto_oids:
                conflicto = srp.load(oid)
                if conflicto.id == conflicto_id:
                    conflicto.eliminar_marcador(lat, lng)
                    srp.save(conflicto)
                    return flask.jsonify(ok=True)

            return flask.jsonify(ok=False, msg="Conflicto no encontrado"), 404

        conflictos = mapa.get_conflictos(srp)
        conflictos_dict = [c.to_dict() for c in conflictos]
        marcadores = {c.id: c.get_marcadores() for c in conflictos}

        return flask.render_template("mapa.html", conflictos=conflictos_dict, marcadores=marcadores)

    except redis.exceptions.ConnectionError:
        if flask.request.method == "GET":
            flask.flash("No se pudo conectar con la base de datos", "danger")
            return flask.redirect(flask.url_for("main.index"))
        else:
            return flask.jsonify(ok=False, msg="Error de conexión con la base de datos"), 500

    except Exception as e:
        if flask.request.method == "GET":
            flask.flash(f"Error al cargar el mapa: {str(e)}", "danger")
            return flask.redirect(flask.url_for("main.index"))
        else:
            return flask.jsonify(ok=False, msg=str(e)), 500
