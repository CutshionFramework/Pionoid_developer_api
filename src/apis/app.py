from flask import Flask
from appstore import appstore
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(appstore)

if __name__ == "__main__":
    app.run(debug=True)
