import flask
import flask_login
import redis
import sirope
from model.UserEntity import UserEntity
from werkzeug.security import generate_password_hash, check_password_hash
from country_list import countries_for_language

# Creamos el blueprint "auth", como módulo independiente
auth_bp = flask.Blueprint("auth", __name__, template_folder="templates", static_folder="static", static_url_path="/auth/static")

@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():

    try:
        srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
        flask.flash("No se pudo conectar con la base de datos para registrarse, inténtalo en otro momento.", "danger")
        return flask.redirect(flask.url_for("main.index"))
    
    # El creador de la librería indica que se use un diccionario pero para poder ordenarlos es mejor convertirlo a tupla.
    countries = sorted(countries_for_language('en'), key=lambda x: x[1])

    if flask.request.method == "POST":
        name = flask.request.form["name"]
        email = flask.request.form["email"]
        pw = flask.request.form["password"]
        country = flask.request.form.get("country") or "unknown"

        if UserEntity.find(srp, email):
            flask.flash("El usuario ya existe.")
        else:
            UserEntity.create(srp, name, email, pw, country)
            flask.flash("Registro exitoso, ya puedes iniciar sesión.", "success")
            return flask.redirect(flask.url_for("auth.login"))

    return flask.render_template("registro.html", countries=countries)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    
    try:
            srp = sirope.Sirope()
    except redis.exceptions.ConnectionError:
            flask.flash("No se pudo conectar con la base de datos para iniciar sesión, inténtalo en otro momento.", "danger")
            return flask.redirect(flask.url_for("main.index"))

    if flask.request.method == "POST":
        email = flask.request.form["email"]
        pw = flask.request.form["password"]
        user = UserEntity.find(srp, email)

        if not user or not check_password_hash(user.password_hash, pw):
            flask.flash("Las credenciales no son válidas.")
        else:
            flask_login.login_user(user)
            return flask.redirect(flask.url_for("main.index"))

    return flask.render_template("login.html")


@auth_bp.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("main.index"))

