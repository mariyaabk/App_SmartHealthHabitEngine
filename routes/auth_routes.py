from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db_manager import DatabaseManager
 
auth_bp = Blueprint("auth", __name__)
db = DatabaseManager()
 
 
@auth_bp.route("/", methods=["GET"])
def index():
    if "user" in session:
        return redirect(url_for("dashboard.home"))
    return redirect(url_for("auth.login"))
 
 
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard.home"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        result   = db.login_user(email, password)
        if result["success"]:
            session["user"] = result["user"]
            return redirect(url_for("dashboard.home"))
        flash(result.get("message", "Email ou mot de passe incorrect."), "error")
    return render_template("auth/login.html")
 
 
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom     = request.form.get("nom", "").strip()
        prenom  = request.form.get("prenom", "").strip()
        email   = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm", "").strip()
 
        if not all([nom, prenom, email, password, confirm]):
            flash("Veuillez remplir tous les champs.", "error")
        elif len(password) < 6:
            flash("Le mot de passe doit faire au moins 6 caractères.", "error")
        elif password != confirm:
            flash("Les mots de passe ne correspondent pas.", "error")
        else:
            result = db.register_user(nom, prenom, email, password)
            if result["success"]:
                flash("Compte créé ! Connectez-vous maintenant. 🎉", "success")
                return redirect(url_for("auth.login"))
            flash(result["message"], "error")
    return redirect(url_for("auth.login"))
 
 
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  OAUTH GOOGLE
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/login/google")
def login_google():
    try:
        from flask import current_app
        oauth = current_app.extensions.get("authlib.integrations.flask_client")
        if oauth is None:
            flash("Google OAuth non configuré.", "error")
            return redirect(url_for("auth.login"))
        return oauth.google.authorize_redirect(url_for("auth.google_callback", _external=True))
    except Exception:
        flash("Connexion Google non disponible.", "error")
        return redirect(url_for("auth.login"))
 
 
@auth_bp.route("/login/google/callback")
def google_callback():
    try:
        from flask import current_app
        oauth = current_app.extensions.get("authlib.integrations.flask_client")
        token     = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            flash("Impossible de récupérer les informations Google.", "error")
            return redirect(url_for("auth.login"))
        result = db.login_or_create_oauth(
            user_info.get("email"),
            user_info.get("given_name", ""),
            user_info.get("family_name", ""),
            provider="google"
        )
        if result["success"]:
            session["user"] = result["user"]
            return redirect(url_for("dashboard.home"))
        flash(result["message"], "error")
    except Exception as e:
        flash(f"Erreur Google OAuth : {str(e)}", "error")
    return redirect(url_for("auth.login"))
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  OAUTH FACEBOOK
# ─────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/login/facebook")
def login_facebook():
    try:
        from flask import current_app
        oauth = current_app.extensions.get("authlib.integrations.flask_client")
        if oauth is None:
            flash("Facebook OAuth non configuré.", "error")
            return redirect(url_for("auth.login"))
        return oauth.facebook.authorize_redirect(url_for("auth.facebook_callback", _external=True))
    except Exception:
        flash("Connexion Facebook non disponible.", "error")
        return redirect(url_for("auth.login"))
 
 
@auth_bp.route("/login/facebook/callback")
def facebook_callback():
    try:
        from flask import current_app
        oauth = current_app.extensions.get("authlib.integrations.flask_client")
        token     = oauth.facebook.authorize_access_token()
        resp      = oauth.facebook.get("https://graph.facebook.com/me?fields=first_name,last_name,id")
        user_info = resp.json()
        email     = f"fb_{user_info.get('id')}@facebook.local"
        result = db.login_or_create_oauth(
            email,
            user_info.get("first_name", ""),
            user_info.get("last_name", ""),
            provider="facebook"
        )
        if result["success"]:
            session["user"] = result["user"]
            return redirect(url_for("dashboard.home"))
        flash(result["message"], "error")
    except Exception as e:
        flash(f"Erreur Facebook OAuth : {str(e)}", "error")
    return redirect(url_for("auth.login"))
 