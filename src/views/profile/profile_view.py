import flask
from flask_login import current_user
import sirope
import redis
from country_list import countries_for_language


profile_bp = flask.Blueprint("profile", __name__, url_prefix='', template_folder="templates", static_folder="static", static_url_path="/profile/static")

@profile_bp.route("/profile/<safe_oid>")
def profile(safe_oid):

    country_names = {name: code for code, name in countries_for_language('en')}

    try:
        srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))

    try:
        user = srp.load(srp.oid_from_safe(safe_oid))
        if not user or user.email != current_user.email:
            raise Exception()
        country_code = country_names.get(user.country, "aq")
        return flask.render_template("profile.html", user=user, country_code=country_code)
    except Exception:
        flask.flash("No se ha podido recuperar el perfil del usuario, inténtelo en otro momento", "danger")
        return flask.redirect(flask.url_for("main.index"))