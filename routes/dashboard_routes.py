from flask import Blueprint, render_template, session, redirect, url_for
from database.db_manager import DatabaseManager
from functools import wraps
from utils.translations import get_t

dashboard_bp = Blueprint("dashboard", __name__)
db = DatabaseManager()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            # If this is a non-GET request (AJAX/fetch), return JSON so frontend can handle it
            from flask import request, jsonify
            if request.method != 'GET':
                return jsonify({"success": False, "redirect": url_for("auth.login")}), 401
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route("/dashboard")
@login_required
def home():
    user  = session["user"]
    t     = get_t(session.get("lang", "fr"))
    stats = db.get_statistiques(user["id"])
    today_done = db.a_deja_repondu_aujourd_hui(user["id"])
    hist  = db.get_historique(user["id"], limit=7)
    return render_template("dashboard/home.html",
                           user=user, t=t, stats=stats,
                           today_done=today_done, historique=hist,
                           current_lang=session.get("lang","fr"))
