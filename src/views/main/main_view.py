import flask

main_bp = flask.Blueprint("main", __name__, template_folder="templates", static_folder="static",static_url_path="/main/static")

@main_bp.route("/")
def index():
    return flask.render_template("index.html")
