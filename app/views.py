from app import app
from flask import request, redirect, url_for, send_from_directory, render_template
import subprocess
import redis
import random
import json
import os
#https://medium.com/@emerico/convert-pdf-to-image-using-python-flask-2864fb655e01


#UPLOAD_FOLDER = '/Users/beatescheibel/Desktop/flask/uploads'
UPLOAD_FOLDER = '/home/bscheibel/uploads_app'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'PDF'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def convert_pdf_img(filename):
    PDFFILE = UPLOAD_FOLDER +"/" + filename
    subprocess.call(['pdftoppm', '-jpeg', '-singlefile',
                     PDFFILE, '/home/bscheibel/uploads_app/out'])

def extract_all(uuid, filename, db):
    #order_bounding_boxes_in_each_block.main(uuid, UPLOAD_FOLDER + "/" + filename)
    subprocess.call(['python3','/home/bscheibel/PycharmProjects/dxf_reader/main.py', str(uuid),UPLOAD_FOLDER + "/" + filename,db])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            uuid = random.randint(100,10000000)
            extract_all(uuid, filename, 'localhost')
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

@app.route('/show/<filename>&<uuid>')
def uploaded_file(filename, uuid):
    file_out = "out.jpg"
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        convert_pdf_img(filename)
        db = redis.Redis("localhost")
        #isos = db.get(uuid+"dims")
        #print(iso)
        isos = json.loads(db.get(uuid+"isos"))
        dims = json.loads(db.get(uuid+"dims"))
        return render_template('show_image.html', filename=file_out, isos=isos, dims=dims)

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


@app.route('/generate/<name>')
def generate(name):
    name = name.replace(" ","")
    url = name+".PDF"
    url1 = "./static/isos/"+url
    print(url1)
    try:
        file = send_from_directory("static/isos",url)
        return file
    except:
        return"Sorry file not found"

@app.route('/show_results', methods=['POST'])
def form_post():
    text = request.args.get("form")
    return render_template('display_results.html', text=text)