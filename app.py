from flask import Flask
from routes import setup_routes
from models import *

app = Flask(__name__)

setup_routes(app)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)