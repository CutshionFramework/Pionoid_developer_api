from flask import Flask
from appstore import appstore

app = Flask(__name__)
app.register_blueprint(appstore)

if __name__ == "__main__":
    app.run(debug=True)
