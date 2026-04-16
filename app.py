# app.py - Application entry point
# TechRent Pro - Equipment Rental Platform

import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, render_template, jsonify, request
from werkzeug.wrappers import Response

from routes import equipment
from routes import customers
from routes import rentals
from routes import api
import db


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
    app.register_blueprint(equipment.equipment_bp)
    app.register_blueprint(customers.customers_bp)
    app.register_blueprint(rentals.rentals_bp)
    app.register_blueprint(api.api_bp)

    # Dashboard route
    @app.route("/")
    def dashboard() -> str:
        """
        Render the main dashboard page.

        Returns:
            Response: Rendered index.html with stats
                      and recent rentals.
        """
        stats = db.get_dashboard_stats()
        recent = db.get_recent_rentals(limit=5)
        return render_template(
            "index.html",
            stats=stats,
            recent_rentals=recent,
        )
    
        # Reports route
    @app.route("/reports")
    def reports() -> str:
        """
        Render the reports and analytics page.

        Returns:
            Response: Rendered reports.html with report data.
        """
        report = db.get_report_data()
        return render_template(
            "reports.html",
            report=report,
        )

    # Error handlers - API paths always return JSON
    @app.errorhandler(400)
    def bad_request(
        error: Exception,
    ) -> tuple[Response, int] | tuple[str, int]:
        """Handle 400 errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Bad request"}), 400
        return render_template("errors/404.html"), 400

    @app.errorhandler(404)
    def page_not_found(
        error: Exception,
    ) -> tuple[Response, int] | tuple[str, int]:
        """Handle 404 errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(
        error: Exception,
    ) -> tuple[Response, int] | tuple[str, int]:
        """Handle 405 errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Method not allowed"}), 405
        return render_template("errors/404.html"), 405

    @app.errorhandler(500)
    def internal_error(
        error: Exception,
    ) -> tuple[Response, int] | tuple[str, int]:
        """Handle 500 errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("errors/500.html"), 500


    return app



def main():
    app = create_app()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    app.run(debug=debug_mode, host=host, port=port)



if __name__ == "__main__":
    main()
