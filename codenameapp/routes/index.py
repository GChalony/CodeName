from flask import render_template, Blueprint
from codenameapp.routes import routes_blueprint


@routes_blueprint.route("/index")
@routes_blueprint.route("/")
def get_home():
    return render_template("index.html")
