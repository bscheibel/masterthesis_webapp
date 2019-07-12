from app import app
from flask import render_template
from flask import request, redirect


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":

        if request.files:

            image = request.files["image"]

            print(image)

            return redirect(request.url)


    return render_template("upload_image.html")
