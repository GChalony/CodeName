from flask import render_template
from codenameapp import app

@app.route("/index")
@app.route("/")
def get_home():
    return render_template("index.html")
