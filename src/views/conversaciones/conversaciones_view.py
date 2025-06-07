import flask
import redis
import sirope

from model.MapEntity import Mapa
from model.ComentaryEntity import Comentario
from model.ConversationEntity import ConversationEntity
from flask_login import current_user

from model.UserEntity import UserEntity

# Blueprint para las rutas relacionadas con el foro de conversaciones
conversaciones_bp = flask.Blueprint("conversaciones", __name__, template_folder="templates", static_folder="static", static_url_path="/conversaciones/static")


@conversaciones_bp.route("/conversaciones", methods=["GET"])
def foro_index():
    """Muestra la página principal del foro con todos los conflictos disponibles.

    :return: Renderiza la plantilla 'conversaciones.html' con la lista de conflictos.
    """
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
    """Muestra y permite crear conversaciones dentro de un conflicto específico.

    :param conflicto_id: ID del conflicto al que se accede.
    :return: Renderiza la plantilla 'foro_conflicto.html' con las conversaciones.
    """
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
            if current_user.is_authenticated:
                title = flask.request.form.get("title")
                content = flask.request.form.get("content")
                autor = current_user.username

                if title and content:
                    nueva = ConversationEntity(title, content, autor)
                    conflicto.añadir_conversacion(nueva, srp)
                    srp.save(conflicto)
                    return flask.redirect(flask.url_for("conversaciones.foro_conflicto", conflicto_id=conflicto.id))
            else:
                flask.flash("Debes iniciar sesión antes de crear una conversación", "danger")
                return flask.redirect(flask.url_for("conversaciones.foro_conflicto", conflicto_id=conflicto.id))

        conversaciones = []
        for conv in conflicto.get_conversaciones(srp):
            comentarios = conv.get_comentarios(srp)
            ult_com = comentarios[-1] if comentarios else None
            conv._soid = srp.safe_from_oid(srp.save(conv))
            conversaciones.append((conv, ult_com))

        return flask.render_template("foro_conflicto.html", conflicto=conflicto, conversaciones=conversaciones)

    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar a la base de datos", "danger")
        return flask.redirect(flask.url_for("main.index"))
    except Exception as e:
        flask.flash(f"Error: {str(e)}", "danger")
        return flask.redirect(flask.url_for("main.index"))


@conversaciones_bp.route("/conversaciones/<conflicto_id>/<conversation_soid>", methods=["GET", "POST"])
def ver_conversacion(conflicto_id, conversation_soid):
    """Muestra una conversación concreta y permite añadir o eliminar comentarios.

    :param conflicto_id: ID del conflicto relacionado.
    :param conversation_soid: OID seguro de la conversación.
    :return: Renderiza 'ver_conversacion.html' con comentarios paginados.
    """
    try:
        srp = sirope.Sirope()
        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")
        conflicto = next((c for c in mapa.get_conflictos(srp) if c.id == conflicto_id), None)
        if not conflicto:
            flask.flash("Conflicto no encontrado", "warning")
            return flask.redirect(flask.url_for("conversaciones.foro_index"))

        conversacion = srp.load(srp.oid_from_safe(conversation_soid))
        if not conversacion:
            flask.flash("Conversación no encontrada", "warning")
            return flask.redirect(flask.url_for("conversaciones.foro_conflicto", conflicto_id=conflicto.id))

        if flask.request.method == "POST":
            if 'contenido' in flask.request.form:
                contenido = flask.request.form.get("contenido")
                autor = current_user.username if current_user.is_authenticated else "Anónimo"
                if contenido:
                    nuevo = Comentario(autor, contenido)
                    conversacion.añadir_comentario(nuevo, srp)
                    srp.save(conversacion)
                    return flask.redirect(flask.url_for("conversaciones.ver_conversacion", conflicto_id=conflicto.id, conversation_soid=conversation_soid))

            elif 'borrar_comentario' in flask.request.form:
                comentario_id = flask.request.form.get("borrar_comentario")
                comentarios = conversacion.get_comentarios(srp)
                for i, c in enumerate(comentarios):
                    if str(c.id) == comentario_id and current_user.is_authenticated and c.autor == current_user.username:
                        comentario_oid = conversacion.comentario_oids[i]
                        conversacion.eliminar_comentario(srp, comentario_oid)
                        srp.save(conversacion)
                        break
                return flask.redirect(flask.url_for("conversaciones.ver_conversacion", conflicto_id=conflicto.id, conversation_soid=conversation_soid))

        comentarios = conversacion.get_comentarios(srp)
        comentarios.sort(key=lambda c: c.fecha)

        page = int(flask.request.args.get("page", 1))
        per_page = 10
        total = len(comentarios)
        start = (page - 1) * per_page
        end = start + per_page
        comentarios_paginados = comentarios[start:end]

        autores_oids = {}
        for c in comentarios_paginados:
            if c.autor not in autores_oids:
                user = srp.find_first(UserEntity, lambda u: u.username == c.autor)
                autores_oids[c.autor] = srp.safe_from_oid(user.__oid__) if user else None

        return flask.render_template(
            "ver_conversacion.html",
            conflicto=conflicto,
            conversacion=conversacion,
            comentarios=comentarios_paginados,
            page=page,
            total_pages=(total + per_page - 1) // per_page,
            autores_oids=autores_oids
        )

    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar a la base de datos", "danger")
        return flask.redirect(flask.url_for("main.index"))
    except Exception as e:
        flask.flash(f"Error: {str(e)}", "danger")
        return flask.redirect(flask.url_for("main.index"))
