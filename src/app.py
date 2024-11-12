import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from src.operations import Endpoints

# Initialize Flask app directly
app = Flask(__name__)
swagger = Swagger(app, template_file=os.path.abspath("./docs/openapi.yml"))

# Initialize CORS
CORS(app)
Endpoints(app)

if __name__ == "__main__":
    app.run(debug=True)
