from app import app

if __name__ == "__main__":
    #app.run()
    server = Flask(__name__, static_url_path="", static_folder="static")