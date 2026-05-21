from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db_manager import DatabaseManager
from models.score_calculator import ScoreCalculator
from routes.dashboard_routes import login_required
from utils.translations import get_t

questionnaire_bp = Blueprint("questionnaire", __name__)
db   = DatabaseManager()
calc = ScoreCalculator()

# Structure des questions (indépendante de la langue — les textes viennent des traductions)
QUESTIONS_META = [
    {"id": "heure_sommeil",   "emoji": "🌙", "type": "slider", "min": 0,  "max": 12,  "step": 0.5, "default": 7,   "unite_key": "unite"},
    {"id": "qualite_sommeil", "emoji": "💤", "type": "choice", "valeurs": [1, 2, 3, 4]},
    {"id": "niveau_stress",   "emoji": "😰", "type": "scale",  "valeurs": [1, 2, 3, 4, 5], "colors": ["#00897b","#66bb6a","#ffd740","#ff7043","#d50000"]},
    {"id": "concentration",   "emoji": "🧠", "type": "scale",  "valeurs": [1, 2, 3, 4, 5], "colors": ["#00897b","#66bb6a","#ffd740","#ff7043","#d50000"]},
    {"id": "humeur",          "emoji": "😊", "type": "scale",  "valeurs": [1, 2, 3, 4, 5], "colors": ["#00897b","#66bb6a","#ffd740","#ff7043","#d50000"]},
    {"id": "sport",           "emoji": "🏃", "type": "slider", "min": 0,  "max": 180, "step": 5,   "default": 0,   "unite_key": "unite"},
    {"id": "temps_ecran",     "emoji": "📱", "type": "slider", "min": 0,  "max": 16,  "step": 0.5, "default": 4,   "unite_key": "unite"},
    {"id": "cafeine",         "emoji": "☕", "type": "slider", "min": 0,  "max": 10,  "step": 1,   "default": 1,   "unite_key": "unite"},
    {"id": "hydratation",     "emoji": "💧", "type": "slider", "min": 0,  "max": 5,   "step": 0.25,"default": 1.5, "unite_key": "unite"},
    {"id": "repas_equilibre", "emoji": "🥗", "type": "choice", "valeurs": [0, 1]},
]


def build_question(idx: int, t: dict) -> dict:
    """Fusionne les métadonnées et les textes traduits pour une question."""
    meta = QUESTIONS_META[idx].copy()
    tq   = t["questions"][idx]
    meta["num"]   = idx + 1
    meta["texte"] = tq["texte"]
    meta["sous"]  = tq["sous"]
    if meta["type"] == "slider":
        meta["unite"] = tq.get("unite", "")
    elif meta["type"] == "choice":
        choix_raw = tq.get("choix", [])
        # Séparer emoji et label
        meta["choix"] = []
        for i, c in enumerate(choix_raw):
            parts = c.split(" ", 1)
            emoji = parts[0] if len(parts) > 1 else ""
            label = parts[1] if len(parts) > 1 else c
            meta["choix"].append((label, emoji, meta["valeurs"][i]))
    elif meta["type"] == "scale":
        labels_raw = tq.get("labels", [])
        meta["labels"] = []
        for i, l in enumerate(labels_raw):
            parts = l.split(" ", 1)
            emoji = parts[0] if len(parts) > 1 else ""
            label = parts[1] if len(parts) > 1 else l
            meta["labels"].append((label, emoji, meta["valeurs"][i]))
    return meta


@questionnaire_bp.route("/questionnaire")
@login_required
def questionnaire():
    user = session["user"]
    t    = get_t(session.get("lang", "fr"))
    if db.a_deja_repondu_aujourd_hui(user["id"]):
        return render_template("questionnaire/already_done.html", user=user, t=t)
    return redirect(url_for("questionnaire.question", idx=0))


@questionnaire_bp.route("/questionnaire/<int:idx>", methods=["GET", "POST"])
@login_required
def question(idx):
    user  = session["user"]
    t     = get_t(session.get("lang", "fr"))
    total = len(QUESTIONS_META)

    if idx >= total:
        return redirect(url_for("questionnaire.submit"))
    if db.a_deja_repondu_aujourd_hui(user["id"]):
        return render_template("questionnaire/already_done.html", user=user, t=t)

    q = build_question(idx, t)

    if request.method == "POST":
        reponses = session.get("questionnaire_reponses", {})
        val = request.form.get("valeur")
        if val is None or val == "":
            return render_template("questionnaire/question.html",
                                   user=user, t=t, q=q, idx=idx, total=total,
                                   error=t["q_error"], prev_val=None,
                                   current_lang=session.get("lang","fr"))
        reponses[q["id"]] = val
        session["questionnaire_reponses"] = reponses
        if idx + 1 >= total:
            return redirect(url_for("questionnaire.submit"))
        return redirect(url_for("questionnaire.question", idx=idx + 1))

    reponses = session.get("questionnaire_reponses", {})
    prev_val = reponses.get(q["id"])
    return render_template("questionnaire/question.html",
                           user=user, t=t, q=q, idx=idx, total=total,
                           error=None, prev_val=prev_val,
                           current_lang=session.get("lang","fr"))


@questionnaire_bp.route("/questionnaire/submit")
@login_required
def submit():
    user     = session["user"]
    t        = get_t(session.get("lang", "fr"))
    reponses = session.get("questionnaire_reponses", {})

    if len(reponses) < len(QUESTIONS_META):
        return redirect(url_for("questionnaire.question", idx=0))

    try:
        data = {
            "heure_sommeil":   float(reponses["heure_sommeil"]),
            "qualite_sommeil": int(reponses["qualite_sommeil"]),
            "niveau_stress":   int(reponses["niveau_stress"]),
            "concentration":   int(reponses["concentration"]),
            "humeur":          int(reponses["humeur"]),
            "sport":           int(reponses["sport"]),
            "temps_ecran":     float(reponses["temps_ecran"]),
            "cafeine":         int(reponses["cafeine"]),
            "hydratation":     float(reponses["hydratation"]),
            "repas_equilibre": int(reponses["repas_equilibre"]),
        }
    except Exception:
        return redirect(url_for("questionnaire.question", idx=0))

    scores   = calc.calculer(data)
    conseils = calc.generer_conseils(data, scores)

    habitude_id = db.save_habitude(user["id"], data)
    db.save_score(user["id"], habitude_id, scores)
    session.pop("questionnaire_reponses", None)

    return render_template("questionnaire/results.html",
                           user=user, t=t, scores=scores, conseils=conseils,
                           current_lang=session.get("lang","fr"))
