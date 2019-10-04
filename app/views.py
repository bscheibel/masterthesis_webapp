#encoding
from app import app
from flask import request, redirect, url_for, send_from_directory, render_template
import subprocess
import redis
import random
import json
import os
import json
import re
import base64
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
    subprocess.call(['python3','/home/bscheibel/PycharmProjects/dxf_reader/main.py', str(uuid),UPLOAD_FOLDER + "/" + filename, db, str(0)])

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
    #file_out = filename
    if request.method == 'POST':
        uuid = 433
    if filename.endswith(".pdf") or filename.endswith(".PDF"):
        convert_pdf_img(filename)
        db = redis.Redis("localhost")
        #isos = db.get(uuid+"dims")
        #print(iso)
        isos = json.loads(db.get(str(uuid)+"isos"))
        dims = json.loads(db.get(str(uuid)+"dims"))
        number_blocks = db.get(str(uuid)+"eps")
        html_code = ""
        reg = r"(-?\d{1,}\.?\d*)"
        for dim in dims:
            html_code += '''<td><h4>''' + dim + '''</h4></td>'''
            for d in dims[dim]:
                number = d

                """ number = re.search(reg, d)
                number = number.group(1)
                try:
                    floats = len(number.split(".")[1])
                    if floats <= 1:
                        steps = 0.1
                    elif floats == 2:
                        steps = 0.01
                    elif floats == 3:
                        steps = 0.001
                    else:
                        steps = 0.001
                except:          """
                steps = 0.1
                coords = ",".join(str(e) for e in dims[dim][d])
                html_code += "<tr><td style='text-align:center'> <input type='checkbox' name='relevant." + d + "' value='checked'> </td>" + \
                             "<td style='text-align:center'>" + d + "</td>" + \
                             "<td style='text-align:center'> <input type='number' step='" + str(steps) + "' data-coords='" + coords + "' name='" + d + "' value='" + number + "'  size='10'> </td></tr>"
                #print(html_code)
        return render_template('show_image.html', filename=file_out, isos=isos, dims=dims, text=html_code, number=number_blocks)

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
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route('/generate/<name>')
def generate(name):
    name = name.replace(" ","")
    url = name+".PDF"
    try:
        file = send_from_directory("static/isos",url)
        return file
    except:
        return"Sorry file not found"

@app.route('/redis/get/<key>',methods=['GET'])
def redis_get(key):
    db = redis.Redis("localhost")
    result = json.loads(db.get(key))
    return result

@app.route('/redis/set/<key>/<value>',methods=['POST'])
def redis_set(key, value):
    db = redis.Redis("localhost")
    try:
        result = json.loads(db.get(key))


        key = key.encode("utf-8")
        result = db.set(key, str(value))
    else:
        db.set( )
    return "OK"

