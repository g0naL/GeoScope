import flask


mapa_bp = flask.Blueprint("mapa", __name__, template_folder="templates", static_folder="static", static_url_path="/mapa/static")

@mapa_bp.route("/mapa", methods=["GET"])
def mapa():
    return None