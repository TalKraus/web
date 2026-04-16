# app.py - Application entry point
# TechRent Pro - Equipment Rental Platform

import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask



def create_app() -> Flask:
    """
    Application factory - creates and configures the Flask app.

    Returns:
        Flask: The configured Flask application.
    """
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())

    # Swagger config
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: rule.rule.startswith("/api/"),
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs",
    }
    swagger_template = {
        "info": {
            "title": "TechRent Pro REST API",
            "version": "1.0.0",
            "description": ("REST API for managing equipment rentals"),
        },
        "basePath": "/api",
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Register blueprints

    return app



def main():
    app = create_app()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(debug=debug_mode, host=host, port=port)



if __name__ == "__main__":
    main()
