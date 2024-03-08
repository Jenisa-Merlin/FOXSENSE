from flask import Flask
from routes import *
from models import *

app = Flask(__name__)
app.secret_key = "abcd@123"

setupRoutes(app)

if __name__ == '__main__':
    #create_tables()
    app.run(debug=True)