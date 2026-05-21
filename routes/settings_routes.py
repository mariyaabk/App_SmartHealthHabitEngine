from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
import logging

logger = logging.getLogger(__name__)
from database.db_manager import DatabaseManager
from database.db_manager import DatabaseManager
from routes.dashboard_routes import login_required
from utils.translations import get_t

settings_bp = Blueprint("settings", __name__)


db = DatabaseManager()


@settings_bp.route("/set_lang/<lang>")
@login_required
def set_lang(lang):
    """Change la langue dans la session Flask et recharge la page précédente."""
    if lang in ("fr", "en"):
        session["lang"] = lang
    referrer = request.referrer or url_for("dashboard.home")
    return redirect(referrer)


@settings_bp.route("/settings")
@login_required
def settings():
    t = get_t(session.get("lang", "fr"))
    return render_template(
        "settings/settings.html",
        user=session["user"],
        t=t,
        current_lang=session.get("lang", "fr"),
    )


@settings_bp.route("/settings/update_profile", methods=["POST"])
@login_required
def update_profile():
    user_id = session["user"]["id"]
    nom    = request.form.get("nom", "").strip()
    prenom = request.form.get("prenom", "").strip()
    email  = request.form.get("email", "").strip()

    if not all([nom, prenom, email]):
        return jsonify({"success": False, "message": "Tous les champs sont requis."})

    result = db.update_profile(user_id, nom, prenom, email)
    if result["success"]:
        session["user"]["nom"]    = nom
        session["user"]["prenom"] = prenom
        session["user"]["email"]  = email
        session.modified = True
    return jsonify(result)

@settings_bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    t = get_t(session.get("lang", "fr"))
    result = db.delete_account(user["id"])
    if result["success"]:
        flash(t.get("account_deleted", "Compte supprimé."), "success")
        session.clear()
        return redirect(url_for("auth.login"))

    flash(result.get("message", t.get("account_delete_error", "Erreur lors de la suppression du compte.")), "error")
    return redirect(url_for("settings.settings"))


@settings_bp.route("/settings/update_notif", methods=["POST"])
@login_required
def update_notif():
    """Sauvegarder email de rappel + heure côté serveur."""
    user_id      = session["user"]["id"]
    email_notif  = request.form.get("email_notif", "").strip()
    reminder_time = request.form.get("reminder_time", "").strip()

    if not email_notif or not reminder_time:
        return jsonify({"success": False, "message": "Email et heure requis."})

    result = db.update_notif_settings(user_id, email_notif, reminder_time)
    if result["success"]:
        session["user"]["email_notif"]   = email_notif
        session["user"]["reminder_time"] = reminder_time
        session.modified = True
    return jsonify(result)
