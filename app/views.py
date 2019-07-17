from app import app
import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from wand.image import Image as wandImage
#https://medium.com/@emerico/convert-pdf-to-image-using-python-flask-2864fb655e01


UPLOAD_FOLDER = '/Users/beatescheibel/Desktop/flask/uploads'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'PDF'])


@app.route("/")
def index():
    return render_template("index.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):

            filename = file.filename
            #image = wandImage(filename=filename)
            #image.save(os.path).join(app.config["UPLOAD_FOLDER"], filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/show/<filename>')
def uploaded_file(filename):
    #filename = 'http://127.0.0.1:5000/uploads/' + filename
    return render_template('show_image.html', filename=filename)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)