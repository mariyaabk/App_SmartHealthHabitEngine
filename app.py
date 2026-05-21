from flask import Flask
from config.settings import (
    SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET
)
from database.db_manager import DatabaseManager
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.questionnaire_routes import questionnaire_bp
from routes.stats_routes import stats_bp
from routes.calendar_routes import calendar_bp
from routes.ai_routes import ai_bp
from routes.rapport_routes import rapport_bp
from routes.settings_routes import settings_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # ── BDD ───────────────────────────────────────────────────────────────────
    db = DatabaseManager()
    db.initialize_database()

    

    # ── OAuth (Google + Facebook) ─────────────────────────────────────────────
    if GOOGLE_CLIENT_ID and FACEBOOK_CLIENT_ID:
        from authlib.integrations.flask_client import OAuth
        oauth = OAuth(app)
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
        oauth.register(
            name="facebook",
            client_id=FACEBOOK_CLIENT_ID,
            client_secret=FACEBOOK_CLIENT_SECRET,
            access_token_url="https://graph.facebook.com/oauth/access_token",
            authorize_url="https://www.facebook.com/dialog/oauth",
            api_base_url="https://graph.facebook.com/",
            client_kwargs={"scope": "public_profile"},
        )

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(questionnaire_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(rapport_bp)
    app.register_blueprint(settings_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "="*55)
    print("  Smart Health Habit Engine — Serveur démarré !")
    print("  Ouvre ton navigateur sur : http://localhost:5000")
    print("="*55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)