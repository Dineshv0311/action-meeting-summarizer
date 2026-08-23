from flask import Flask
from flask_cors import CORS
from app.core.config import settings
from app.api.v1.routes import api_v1_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = settings.max_content_length_bytes
    
    CORS(app)
    app.register_blueprint(api_v1_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "healthy"}, 200

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=settings.PORT, debug=(settings.FLASK_ENV == "development"))