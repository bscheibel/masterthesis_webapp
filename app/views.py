from app import app
import os
from flask import make_response
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import subprocess
import order_bounding_boxes_in_each_block
import redis
import random
import json
#https://medium.com/@emerico/convert-pdf-to-image-using-python-flask-2864fb655e01


#UPLOAD_FOLDER = '/Users/beatescheibel/Desktop/flask/uploads'
UPLOAD_FOLDER = '/home/bscheibel/uploads_app'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'PDF'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):

            filename = file.filename
            #image = wandImage(filename=filename)
            #image.save(os.path).join(app.config["UPLOAD_FOLDER"], filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            uuid = random.randint(100,10000000)
            order_bounding_boxes_in_each_block.main(uuid, UPLOAD_FOLDER+"/"+filename)
            return redirect(url_for('uploaded_file', filename=filename, uuid=uuid))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
def convert_pdf(filename):
    PDFFILE = UPLOAD_FOLDER +"/" + filename
    subprocess.call(['pdftoppm', '-jpeg', '-singlefile',
                     PDFFILE, '/home/bscheibel/uploads_app/out'])

@app.route('/show/<filename>&<uuid>')
def uploaded_file(filename, uuid):
    file_out = "out.jpg"
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        convert_pdf(filename)
        db = redis.Redis("localhost")
        #uuid = "dd"
        isos = json.loads(db.get(uuid))
        return render_template('show_image.html', filename=file_out, isos=isos)

    else:
        filename = filename
        return render_template('show_image.html', filename=filename)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

