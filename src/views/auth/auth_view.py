import flask
import flask_login
import redis
import sirope
from model.UserEntity import UserEntity
from country_list import countries_for_language
import pytz

auth_bp = flask.Blueprint("auth", __name__, template_folder="templates", static_folder="static", static_url_path="/auth/static")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Gestiona el registro de nuevos usuarios.

    Si la solicitud es GET, muestra el formulario de registro.
    Si es POST, valida los datos y crea el usuario si no existe.

    :return: Plantilla de registro o redirección.
    """
    try:
        srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos para registrarse, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))

    countries = sorted(countries_for_language('en'), key=lambda x: x[1])

    if flask.request.method == "POST":
        name = flask.request.form["name"]
        username = flask.request.form["username"]
        email = flask.request.form["email"]
        pw = flask.request.form["password"]
        country = flask.request.form.get("country") or "unknown"
        timezone = flask.request.form["timezone"]
        language = flask.request.form["language"]

        if UserEntity.find_by_mail(srp, email):
            flask.flash("El correo electrónico ya está asociada a otra cuenta.", "danger")
        else:
            UserEntity.create(srp, name, email, pw, country, username, language, timezone)
            flask.flash("Registro exitoso, ya puedes iniciar sesión.", "success")
            return flask.redirect(flask.url_for("auth.login"))

    return flask.render_template("registro.html", countries=countries, timezones=pytz.all_timezones)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Gestiona el inicio de sesión de los usuarios.

    Verifica credenciales y establece la sesión de usuario si son válidas.

    :return: Plantilla de login o redirección.
    """
    try:
        srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos para iniciar sesión, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))

    if flask.request.method == "POST":
        email = flask.request.form["email"]
        pw = flask.request.form["password"]
        user = UserEntity.find_by_mail(srp, email)

        if not user or not user.check_password(pw):
            flask.flash("Las credenciales no son válidas.", "danger")
        else:
            user.set_last_login_now()
            srp.save(user)
            flask_login.login_user(user)
            return flask.redirect(flask.url_for("main.index"))

    return flask.render_template("login.html")


@auth_bp.route("/logout")
@flask_login.login_required
def logout():
    """Finaliza la sesión actual del usuario.

    :return: Redirección a la página de inicio.
    """
    flask_login.logout_user()
    return flask.redirect(flask.url_for("main.index"))
