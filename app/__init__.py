from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.debug = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

from app import views
