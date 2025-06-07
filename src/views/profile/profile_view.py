import flask
import flask_login
import sirope
import redis
from country_list import countries_for_language
import pytz

profile_bp = flask.Blueprint("profile", __name__, url_prefix='', template_folder="templates", static_folder="static", static_url_path="/profile/static")

@profile_bp.route("/profile/<safe_oid>")
def profile(safe_oid):
    from model.MapEntity import Mapa
    from model.ConversationEntity import ConversationEntity

    country_names = {name: code for code, name in countries_for_language('en')}

    try:
        srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))

    try:
        user = srp.load(srp.oid_from_safe(safe_oid))
        country_code = country_names.get(user.country, "aq")

        # Buscar comentarios del usuario
        mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")
        comentarios_usuario = []

        if mapa:
            for conflicto in mapa.get_conflictos(srp):
                for conversacion in conflicto.get_conversaciones(srp):
                    comentarios = conversacion.get_comentarios(srp)
                    for i, c in enumerate(comentarios):
                        if c.autor == user.username:
                            c.conflicto_id = conflicto.id
                            c.conversacion_soid = srp.safe_from_oid(srp.save(conversacion))
                            comentarios_usuario.append(c)

        comentarios_usuario.sort(key=lambda c: c.fecha, reverse=True)

        return flask.render_template(
            "profile.html",
            user=user,
            country_code=country_code,
            comentarios=comentarios_usuario
        )

    except Exception:
        flask.flash("No se ha podido recuperar el perfil del usuario, inténtelo en otro momento", "danger")
        return flask.redirect(flask.url_for("main.index"))


@profile_bp.route("/editar-perfil/<safe_oid>", methods=["GET", "POST"])
@flask_login.login_required
def editar_perfil(safe_oid):
    from model.MapEntity import Mapa
    from model.UserEntity import UserEntity

    country_names = {name: code for code, name in countries_for_language('en')}

    try:
        srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))

    try:
        user = srp.load(srp.oid_from_safe(safe_oid))

        if not user or user.email != flask_login.current_user.email:
            raise Exception()

        if flask.request.method == "POST":
            if flask.request.form.get("delete_account"):
                # Cerrar sesión primero
                flask_login.logout_user()

                # Eliminar comentarios
                mapa = srp.find_first(Mapa, lambda m: m.id == "world_map")
                if mapa:
                    for conflicto in mapa.get_conflictos(srp):
                        for conversacion in conflicto.get_conversaciones(srp):
                            comentarios = conversacion.get_comentarios(srp)
                            for i, c in reversed(list(enumerate(comentarios))):
                                if c.autor == user.username:
                                    comentario_oid = conversacion.comentario_oids[i]
                                    conversacion.eliminar_comentario(srp, comentario_oid)
                            srp.save(conversacion)

                # Eliminar el usuario
                srp.delete(user.oid)

                flask.flash("Tu cuenta ha sido eliminada permanentemente.", "info")
                return flask.redirect(flask.url_for("main.index"))


            # Actualizar perfil
            user.name = flask.request.form.get("name", user.name)
            user.username = flask.request.form.get("username", user.username)
            user.bio = flask.request.form.get("bio", user.bio)
            user.language = flask.request.form.get("language", user.language)
            user.timezone = flask.request.form.get("timezone", user.timezone)
            srp.save(user)
            flask.flash("Perfil actualizado correctamente.", "success")
            return flask.redirect(flask.url_for("profile.profile", safe_oid=safe_oid))

        country_code = country_names.get(user.country, "aq")
        return flask.render_template("editar-perfil.html", user=user, country_code=country_code, safe_oid=safe_oid, timezones=pytz.all_timezones)
    
    except Exception:
        flask.flash("No se ha podido recuperar el perfil de usuario.", "danger")
        return flask.redirect(flask.url_for("main.index"))

