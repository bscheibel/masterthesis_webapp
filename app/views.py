#encoding
from app import app
from flask import request, redirect, url_for, send_from_directory, render_template
import subprocess
import redis
import random
import PyPDF2
import os
import json
import re
import base64

#path = "/home/bscheibel/app/app"
path = "/home/centurio/Projects/engineering_drawings_ui/app/app"

#path_extraction = '/home/bscheibel/PycharmProjects/dxf_reader/main.py'
path_extraction = "/home/centurio/Projects/engineering_drawings_extraction/main.py"
UPLOAD_FOLDER = path + "/temporary"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'PDF'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def convert_pdf_img(filename):
    PDFFILE = UPLOAD_FOLDER +"/" + filename
    subprocess.call(['pdftoppm', '-jpeg', '-singlefile',
                     PDFFILE, path + '/temporary/out'])

def extract_all(uuid, filename, db):
    subprocess.call(['python3', path_extraction, str(uuid),UPLOAD_FOLDER + "/" + filename, db, str(0)])

def get_file_size(file):
    pdf = PyPDF2.PdfFileReader(file)
    p = pdf.getPage(0)

    w = p.mediaBox.getWidth()
    h= p.mediaBox.getHeight()
    OrientationDegrees = p.get('/Rotate')
    if OrientationDegrees != 0 :
        orientation = "landscape"
    else:
        orientation = "portrait"

    print(w,h,OrientationDegrees)
    return w,h, orientation

def check_links(isos):
    link_names = {}
    isos_names = []
    isos = list(set(isos))
    reg_isos = r"(ISO\s\d*)\s1\-(\d?)"
    print(isos)
    isos_new = []
    for name in isos:
        if re.search(reg_isos, name):
            n = 1
            new_isos = re.search(reg_isos,name).group(1)
            number = re.search(reg_isos,name).group(2)
            while n <= int(number):
                isos_new.append(new_isos+"-"+str(n))
                n += 1
        else:
            isos_new.append(name)
    for name in isos_new:
        try:
            name = name.replace(" ", "")
            url1 = name + ".PDF"
            url = "isos/" + url1
            link_names[name] = url
        except:
            isos_names.append(name)
    return link_names, isos_names


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,app.config["UPLOAD_FOLDER"], filename))
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
        w,h, orientation = get_file_size(UPLOAD_FOLDER +"/" + filename)
        convert_pdf_img(filename)
        db = redis.Redis("localhost")
        gen_tol = db.get(str(uuid)+"tol")
        print(gen_tol)
        isos = json.loads(db.get(str(uuid)+"isos"))
        links, isos_names = check_links(isos)
        dims = json.loads(db.get(str(uuid)+"dims"))
        details = json.loads(db.get(str(uuid) + "details"))
        number_blocks = db.get(str(uuid)+"eps")
        html_code = "General tolerances according to: " + gen_tol + "<br>"
        html_general = ""
        reg = r"(-?\d{1,}\.?\d*)"
        det_coords= "0,0,0,0"
        with open(path+ '/config.json') as f:
            config_file = json.load(f)

        for dim in sorted(dims):
            for det in details:
                try:
                    if dim == det:
                        det_coords = details[det]
                        det_coords = ",".join(str(det) for det in det_coords)
                except:
                    det_coords = "0,0,0,0"
            if "ZZZZ" in dim:
                for d in dims[dim]:
                    html_general += d + "<br>"
                continue
            else:
                html_code += "<td><h4>" + dim + "</h4></td>"
            for d in dims[dim]:
                relevant_isos = []
                search_terms = {}
                terms = ''
                for conf in config_file:
                    if re.search(conf,d):
                        iso = config_file[conf]
                        for key in iso:
                            relevant_isos.append(key)
                            for blub in iso[key]:
                                search_terms[blub] = iso[key][blub]
                        if len(search_terms) < 1:
                            search_terms["Beginn"] = 1
                        terms = json.dumps(search_terms)
                        terms = base64.b64encode(terms.encode())
                try:
                    number = re.search(reg, d)
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
                    except:
                        steps = 0.1
                except:
                    number = d
                    steps = 0.1
                coords = ",".join(str(e) for e in dims[dim][d])
                html_code += "<tr><td style='text-align:center'> <input type='checkbox' name='relevant." + d + "' value='checked'> </td>" + \
                             "<td style='text-align:center'>" + d + "</td>" + \
                             "<td max='3' style='text-align:center'> <input type='number' step='" + str(steps) + "' data-coords='" + coords + " 'data-details='" + det_coords  +"'' name='" + d + "' value='" + number + "'> </td>"

                relevant_isos = list(set(relevant_isos))
                for x in relevant_isos:
                    html_code += "<td style='text-align:left' data-terms='" + terms + "'> <a onclick=ui_add_tab_active('#main','" + x.partition(".")[0] + "','" + x.partition(".")[0] +"',true,'isotab','"+terms+"')>" + x.partition(".")[0] + "</a>  </td>"
                html_code += "</tr>"
                html_links = ""
                for link in links:
                    html_links += "<a onclick =ui_add_tab_active('#main','" + link + "','" + link +"',true,'isotab','empty')> Open " + link + "</a> <br>"
        return render_template('index.html', filename=file_out, isos=isos, dims=dims, text=html_code,html_general=html_general, number=number_blocks, og_filename=filename, w=w, h=h, html_links=html_links, isos_names=isos_names, orientation=orientation)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response



@app.route('/redis/get/<key>',methods=['GET'])
def redis_get(key):
    db = redis.Redis(unix_socket_path='/tmp/redis.sock',db=7)
    result = json.loads(db.get(key))
    return result

@app.route('/redis/set/<key>',methods=['POST'])
def redis_set(key):
    value = request.get_json(force=True)
    value = value["value"]
    db = redis.Redis(unix_socket_path='/tmp/redis.sock',db=7)

    value_name = value[0]
    value_v = value[1]
    try:
        result = json.loads(db.get(key))
        result[value_name] = value_v
        json_res = json.dumps(result)
        db.set(key,json_res)
    except:
        dict_res = {}
        dict_res[value_name] = value_v
        json_dict = json.dumps(dict_res)
        db.set(key, json_dict)
    return "OK"

