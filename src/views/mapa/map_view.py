import flask
import redis
import sirope

from model.MapEntity import Mapa
from model.ConflictEntity import Conflicto

# Se define el blueprint para las rutas relacionadas con el mapa
mapa_bp = flask.Blueprint("mapa", __name__, template_folder="templates", static_folder="static", static_url_path="/mapa/static")

@mapa_bp.route("/mapa", methods=["GET", "POST", "DELETE"])
def mostrar_mapa():
    """Muestra el mapa, añade marcadores o los elimina según el método HTTP.

    :return: Una plantilla renderizada o una respuesta JSON, dependiendo del método.
    """
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
            """Añade un nuevo marcador al conflicto correspondiente.

            :request json: conflicto_id, lat, lng, texto, icono
            :return: Respuesta JSON de éxito o error.
            """
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
            """Elimina un marcador de un conflicto por coordenadas.

            :request json: conflicto_id, lat, lng
            :return: Respuesta JSON de éxito o error.
            """
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

        # GET: renderizar la página del mapa
        conflictos = mapa.get_conflictos(srp)
        conflictos_dict = [c.to_dict() for c in conflictos]
        marcadores = {c.id: c.get_marcadores() for c in conflictos}

        return flask.render_template("mapa.html", conflictos=conflictos_dict, marcadores=marcadores)

    except redis.exceptions.ConnectionError:
        """Manejo de error por fallo en la conexión con Redis."""
        if flask.request.method == "GET":
            flask.flash("No se pudo conectar con la base de datos", "danger")
            return flask.redirect(flask.url_for("main.index"))
        else:
            return flask.jsonify(ok=False, msg="Error de conexión con la base de datos"), 500

    except Exception as e:
        """Manejo de cualquier otro error inesperado."""
        if flask.request.method == "GET":
            flask.flash(f"Error al cargar el mapa: {str(e)}", "danger")
            return flask.redirect(flask.url_for("main.index"))
        else:
            return flask.jsonify(ok=False, msg=str(e)), 500
