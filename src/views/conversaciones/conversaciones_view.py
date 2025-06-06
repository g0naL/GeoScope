import datetime
import flask
import redis
import sirope

from model.MapEntity import Mapa
from model.ConflictEntity import Conflicto
from model.ConversationEntity import ConversationEntity

conversaciones_bp = flask.Blueprint("conversaciones", __name__, template_folder="templates", static_folder="static", static_url_path="/conversaciones/static")

@conversaciones_bp.route("/conversaciones", methods=["GET"])
def foro_index():
    try:
        srp = sirope.Sirope()

        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")
        if not mapa:
            flask.flash("No se encontró el mapa", "danger")
            return flask.redirect(flask.url_for("main.index"))

        conflictos = mapa.get_conflictos(srp)

        return flask.render_template("conversaciones.html", conflictos=conflictos)

    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar a la base de datos", "danger")
        return flask.redirect(flask.url_for("main.index"))
    except Exception as e:
        flask.flash(f"Error al cargar el foro: {str(e)}", "danger")
        return flask.redirect(flask.url_for("main.index"))


@conversaciones_bp.route("/conversaciones/<conflicto_id>", methods=["GET", "POST"])
def foro_conflicto(conflicto_id):
    try:
        srp = sirope.Sirope()

        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")
        if not mapa:
            flask.flash("No se encontró el mapa", "danger")
            return flask.redirect(flask.url_for("main.index"))

        conflicto = next((c for c in mapa.get_conflictos(srp) if c.id == conflicto_id), None)
        if not conflicto:
            flask.flash("Conflicto no encontrado", "warning")
            return flask.redirect(flask.url_for("conversaciones.foro_index"))

        if flask.request.method == "POST":
            title = flask.request.form.get("title")
            content = flask.request.form.get("content")
            autor = flask.request.form.get("autor") or "Anónimo"

            if title and content:
                nueva = ConversationEntity(title, content, autor)
                conflicto.añadir_conversacion(nueva, srp)
                srp.save(conflicto)
                flask.flash("Conversación añadida correctamente", "success")
                return flask.redirect(flask.url_for("conversaciones.foro_conflicto", conflicto_id=conflicto.id))

        conversaciones = []
        for conv in conflicto.get_conversaciones(srp):
            comentarios = conv.get_comentarios(srp)
            ult_com = comentarios[-1] if comentarios else None
            conv._oid = srp.save(conv)
            conversaciones.append((conv, ult_com))

        return flask.render_template("foro_conflicto.html", conflicto=conflicto, conversaciones=conversaciones)
    
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar a la base de datos", "danger")
        return flask.redirect(flask.url_for("main.index"))
    except Exception as e:
        flask.flash(f"Error: {str(e)}", "danger")
        return flask.redirect(flask.url_for("main.index"))


@conversaciones_bp.route("/conversaciones/<conflicto_id>/<conversation_oid>", methods=["GET", "POST"])
def ver_conversacion(conflicto_id, conversation_oid):
    try:
        srp = sirope.Sirope()

        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")
        conflicto = next((c for c in mapa.get_conflictos(srp) if c.id == conflicto_id), None)
        if not conflicto:
            flask.flash("Conflicto no encontrado", "warning")
            return flask.redirect(flask.url_for("conversaciones.foro_index"))

        conversacion = srp.load(sirope.OID.from_str(conversation_oid))
        if not conversacion:
            flask.flash("Conversación no encontrada", "warning")
            return flask.redirect(flask.url_for("conversaciones.foro_conflicto", conflicto_id=conflicto.id))

        if flask.request.method == "POST":
            autor = flask.request.form.get("author")
            texto = flask.request.form.get("text")
            if autor and texto:
                conversacion.comments.append({
                    "author": autor,
                    "text": texto,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                srp.save(conversacion)
                flask.flash("Comentario añadido", "success")
                return flask.redirect(flask.url_for("conversaciones.ver_conversacion", conflicto_id=conflicto.id, conversation_oid=conversation_oid))

        return flask.render_template("ver_conversacion.html", conflicto=conflicto, conversacion=conversacion)
    
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar a la base de datos", "danger")
        return flask.redirect(flask.url_for("main.index"))
    except Exception as e:
        flask.flash(f"Error: {str(e)}", "danger")
        return flask.redirect(flask.url_for("main.index"))


