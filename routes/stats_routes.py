from utils.translations import get_t
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, send_file
from database.db_manager import DatabaseManager
from models.score_calculator import ScoreCalculator
from routes.dashboard_routes import login_required
import json, calendar, datetime


stats_bp = Blueprint("stats", __name__)
db = DatabaseManager()

@stats_bp.route("/stats")
@login_required
def stats():
    user = session["user"]
    historique = db.get_historique(user["id"], limit=30)
    statistiques = db.get_statistiques(user["id"])

    # Préparer les données JSON pour Chart.js
    hist_reversed = list(reversed(historique))
    chart_labels  = [r["date_score"] for r in hist_reversed]
    chart_global  = [r["score_global"]       for r in hist_reversed]
    chart_sommeil = [r["score_sommeil"]       for r in hist_reversed]
    chart_stress  = [r["score_stress"]        for r in hist_reversed]
    chart_activite= [r["score_activite"]      for r in hist_reversed]
    chart_nutrition=[r["score_nutrition"]     for r in hist_reversed]
    chart_conc    = [r["score_concentration"] for r in hist_reversed]

    t = get_t(session.get("lang","fr"))
    return render_template("stats/stats.html",
        user=user, t=t, historique=historique, statistiques=statistiques, current_lang=session.get("lang","fr"),
        chart_labels=json.dumps(chart_labels),
        chart_global=json.dumps(chart_global),
        chart_sommeil=json.dumps(chart_sommeil),
        chart_stress=json.dumps(chart_stress),
        chart_activite=json.dumps(chart_activite),
        chart_nutrition=json.dumps(chart_nutrition),
        chart_conc=json.dumps(chart_conc),
    )


# Calendrier 
calendar_bp = Blueprint("calendrier", __name__)

@calendar_bp.route("/calendar")
@calendar_bp.route("/calendar/<int:year>/<int:month>")
@login_required
def cal(year=None, month=None):
    user = session["user"]
    today = datetime.date.today()
    year  = year  or today.year
    month = month or today.month

    historique = db.get_historique(user["id"], limit=365)
    scores_par_date = {}
    for row in historique:
        d = row["date_score"]
        scores_par_date[str(d)] = row["score_global"]

    cal_data  = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Navigation
    prev_month = month - 1 or 12
    prev_year  = year - (1 if month == 1 else 0)
    next_month = (month % 12) + 1
    next_year  = year + (1 if month == 12 else 0)

    t = get_t(session.get("lang","fr"))
    return render_template("calendar/calendar.html", t=t, current_lang=session.get("lang","fr"),
        user=user, cal_data=cal_data, year=year, month=month,
        month_name=month_name, today=str(today),
        scores_par_date=scores_par_date,
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month,
    )


#  Assistant IA 
ai_bp = Blueprint("ai", __name__)
calc = ScoreCalculator()

@ai_bp.route("/assistant")
@login_required
def assistant():
    user = session["user"]
    historique = db.get_historique(user["id"], limit=14)
    conv_hist  = db.get_conversations_ia(user["id"], limit=10)
    t = get_t(session.get("lang","fr"))
    return render_template("ai/assistant.html", t=t, current_lang=session.get("lang","fr"), user=user,
                           historique=historique, conv_hist=list(reversed(conv_hist)))

@ai_bp.route("/assistant/ask", methods=["POST"])
@login_required
def ask():
    user     = session["user"]
    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"reponse": "Veuillez poser une question."})

    historique = db.get_historique(user["id"], limit=14)
    reponse    = _reponse_ia(question, historique, user)
    db.save_conversation_ia(user["id"], question, reponse)
    return jsonify({"reponse": reponse})


def _reponse_ia(question: str, historique: list, user: dict) -> str:
    """
    Moteur IA hybride :
    1. OpenAI GPT si clé configurée
    2. Moteur de règles étendu — répond à TOUT ce qui touche la santé
    """
    from config.settings import OPENAI_API_KEY
    prenom = user.get("prenom", "")

    # Contexte utilisateur 
    has_data = bool(historique)
    if has_data:
        def moy(key):
            vals = [r[key] for r in historique if r.get(key) is not None]
            return sum(vals) / len(vals) if vals else 0
        mg  = moy("score_global");    ms  = moy("score_sommeil")
        mst = moy("score_stress");    ma  = moy("score_activite")
        mn  = moy("score_nutrition"); mc  = moy("score_concentration")
        nb  = len(historique)
        # Tendance (dernière semaine vs semaine précédente)
        if nb >= 4:
            recent = sum(r["score_global"] for r in historique[:nb//2]) / (nb//2)
            older  = sum(r["score_global"] for r in historique[nb//2:]) / (nb - nb//2)
            tendance = "📈 en hausse" if recent > older + 3 else ("📉 en baisse" if recent < older - 3 else "➡️ stable")
        else:
            tendance = "➡️ stable"
        dims = [("sommeil",ms),("anti-stress",mst),("concentration",mc),("activité",ma),("nutrition",mn)]
        point_fort  = max(dims, key=lambda x: x[1])
        point_faible = min(dims, key=lambda x: x[1])
        ctx_user = (
            f"Données de {prenom} ({nb} derniers jours) :\n"
            f"  Score global : {mg:.1f}/100 ({tendance})\n"
            f"  Sommeil {ms:.0f} | Stress {mst:.0f} | Conc. {mc:.0f} | Activité {ma:.0f} | Nutrition {mn:.0f}\n"
            f"  Point fort : {point_fort[0]} ({point_fort[1]:.0f}) | À améliorer : {point_faible[0]} ({point_faible[1]:.0f})"
        )
    else:
        ctx_user = f"Aucune donnée disponible pour {prenom} — questionnaire non rempli."

    # OpenAI si disponible 
    if OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content":
                        "Tu es un assistant de santé et bien-être bienveillant et expert. "
                        "Tu réponds en français de façon chaleureuse, personnalisée et scientifiquement fondée. "
                        "Tu peux répondre à TOUTES les questions liées à la santé : sommeil, nutrition, sport, "
                        "stress, santé mentale, vitamines, maladies courantes, posture, hydratation, etc. "
                        "Pour les questions médicales graves, tu recommandes toujours un médecin. "
                        "Utilise des emojis pour rendre la réponse agréable. Sois concis (max 200 mots).\n\n"
                        f"Contexte utilisateur :\n{ctx_user}"},
                    {"role": "user", "content": question}
                ], max_tokens=450, temperature=0.7
            )
            return resp.choices[0].message.content
        except Exception:
            pass  # Fallback sur le moteur de règles

    # Moteur de règles étendu 
    q = question.lower().strip()

    def score_ctx(dim_score, label):
        niveau = "excellent" if dim_score >= 80 else "bon" if dim_score >= 65 else "moyen" if dim_score >= 50 else "faible"
        return f"(ton score {label} : **{dim_score:.0f}/100** — {niveau})"

    # Sans données
    if not has_data:
        if any(w in q for w in ["bonjour","salut","hello","hi","coucou"]):
            return f"Bonjour {prenom} ! 👋 Je suis ton assistant santé. Commence par remplir ton **questionnaire** pour que je puisse analyser tes habitudes !"
        return (
            f"Bonjour {prenom} ! 😊 Remplis d'abord ton questionnaire quotidien pour que je puisse "
            f"t'offrir des recommandations vraiment personnalisées.\n\n"
            f"En attendant, je peux te donner des conseils généraux sur :\n"
            f"• 🌙 Le sommeil\n• 🏃 Le sport\n• 🥗 La nutrition\n• 😌 La gestion du stress\n• 💧 L'hydratation"
        )

    # Salutations 
    if any(w in q for w in ["bonjour","salut","hello","hi","coucou","bonsoir"]):
        heure_msg = "Bonne journée" if __import__('datetime').datetime.now().hour < 18 else "Bonne soirée"
        return (
            f"{heure_msg} {prenom} ! 😊\n\n"
            f"Ton score global actuel est de **{mg:.0f}/100** ({tendance}).\n"
            f"💪 Point fort : **{point_fort[0]}**\n"
            f"📌 À travailler : **{point_faible[0]}**\n\n"
            f"Comment puis-je t'aider aujourd'hui ?"
        )

    # Bilan / analyse 
    if any(w in q for w in ["analyse","bilan","résumé","résultats","comment je","comment vais","comment vas","global","général","rapport","vue d'ensemble"]):
        niv = "Excellent 🌟" if mg >= 85 else "Bon 👍" if mg >= 70 else "Moyen ⚠️" if mg >= 50 else "Faible ❌"
        return (
            f"📊 **Bilan complet de {prenom}** ({nb} jours)\n\n"
            f"Score global : **{mg:.1f}/100** — {niv} ({tendance})\n\n"
            f"┌─────────────────────────────┐\n"
            f"│ 🌙 Sommeil        {ms:>5.0f}/100 │\n"
            f"│ 😌 Anti-stress    {mst:>5.0f}/100 │\n"
            f"│ 🧠 Concentration  {mc:>5.0f}/100 │\n"
            f"│ 🏃 Activité       {ma:>5.0f}/100 │\n"
            f"│ 🥗 Nutrition      {mn:>5.0f}/100 │\n"
            f"└─────────────────────────────┘\n\n"
            f"💪 Point fort : **{point_fort[0]}** ({point_fort[1]:.0f}/100)\n"
            f"🎯 Priorité : améliorer ton **{point_faible[0]}** ({point_faible[1]:.0f}/100)"
        )

    # Sommeil 
    if any(w in q for w in ["sommeil","dormir","endormir","réveil","insomnie","sieste","fatigue","reposé","nuit"]):
        ctx = score_ctx(ms, "sommeil")
        if ms >= 75:
            return f"🌙 Ton sommeil est en bonne forme {ctx} !\n\nQuelques astuces pour le maintenir :\n• Garde une heure de coucher fixe (même le week-end)\n• Maintiens ta chambre fraîche (18-19°C)\n• Évite la caféine après 14h"
        return (
            f"🌙 Ton sommeil mérite attention {ctx}\n\n"
            f"**Plan d'amélioration :**\n"
            f"• 📱 Pas d'écran 1h avant de dormir (lumière bleue perturbatrice)\n"
            f"• 🕐 Coucher et lever à heures fixes (même weekend)\n"
            f"• 🌡️ Chambre à 18-19°C (température optimale)\n"
            f"• ☕ Pas de caféine après 14h\n"
            f"• 📚 10 min de lecture calme avant de dormir\n"
            f"• 🫁 Respiration 4-7-8 pour s'endormir plus vite\n\n"
            f"🎯 Objectif : 7 à 9 heures de sommeil de qualité."
        )

    #Stress / anxiété 
    if any(w in q for w in ["stress","anxieux","anxiété","anxieuse","pression","surmenage","burn","burnout","overwhelm","débordé","angoisse"]):
        ctx = score_ctx(mst, "anti-stress")
        if mst >= 70:
            return f"😌 Tu gères bien ton stress {ctx} ! Continue avec tes bonnes habitudes — régularité et sport y contribuent beaucoup."
        return (
            f"😰 Ton niveau de stress est préoccupant {ctx}\n\n"
            f"**Techniques scientifiquement prouvées :**\n"
            f"• 🫁 Respiration 4-7-8 : inspire 4s, retiens 7s, expire 8s — 3x\n"
            f"• 🚶 30 min de marche quotidienne (libère des endorphines)\n"
            f"• 🧘 Méditation 10 min/jour (apps : Petit Bambou, Headspace)\n"
            f"• ✍️ Journal de gratitude le soir (3 choses positives)\n"
            f"• 📵 Limiter les réseaux sociaux (source de stress chronique)\n"
            f"• 🌿 Magnésium B6 (souvent déficient en cas de stress)\n\n"
            f"⚕️ Si le stress dure plus de 2 semaines, consulte un professionnel."
        )

    #  Énergie / vitalité 
    if any(w in q for w in ["énergie","energie","vitalité","dynamisme","épuisé","épuisement","fatigué","fatiguée","coup de pompe","coup de barre"]):
        pf = min(dims, key=lambda x: x[1])
        return (
            f"⚡ **Booster ton énergie — plan personnalisé**\n\n"
            f"Ta priorité #1 : améliore ton **{pf[0]}** ({pf[1]:.0f}/100)\n\n"
            f"**Actions rapides :**\n"
            f"• 💧 2L d'eau/jour (la déshydratation -20% d'énergie)\n"
            f"• ☀️ Lumière naturelle le matin (règle le rythme circadien)\n"
            f"• 🏃 20 min de sport → +65% d'énergie perçue (études)\n"
            f"• 🍎 Évite les pics glycémiques (sucre rapide → crash)\n"
            f"• 😴 Si score sommeil < 65 → priorité absolue au repos\n"
            f"• ☕ Pas plus de 2 cafés/jour, pas après 14h\n"
            f"• 💊 Pense à vérifier tes niveaux de vitamine D et fer"
        )

    #Sport / activité physique
    if any(w in q for w in ["sport","exercice","activité physique","gym","marche","courir","course","musculation","cardio","yoga","pilates","vélo","natation","bouger","sédentaire"]):
        ctx = score_ctx(ma, "activité")
        if ma >= 75:
            return f"🏃 Tu es bien actif(ve) {ctx} ! Pense à varier les exercices et à soigner ta récupération (sommeil, protéines, étirements)."
        return (
            f"🏃 **Plan activité physique personnalisé** {ctx}\n\n"
            f"**Progression recommandée :**\n"
            f"• Semaine 1-2 : 15 min de marche rapide/jour\n"
            f"• Semaine 3-4 : 30 min marche ou vélo\n"
            f"• Mois 2 : + 2 séances renforcement musculaire/semaine\n\n"
            f"**L'OMS recommande :** 150 min d'activité modérée/semaine\n\n"
            f"**Bénéfices prouvés :**\n"
            f"• -35% risque cardiovasculaire\n"
            f"• -30% anxiété et dépression\n"
            f"• +40% qualité du sommeil\n"
            f"• +20% concentration et mémoire"
        )

    #Nutrition / alimentation 
    if any(w in q for w in ["nutrition","manger","alimentation","nourriture","régime","diet","repas","calorie","protéine","glucide","lipide","légume","fruit","végétarien","vegan","sucre","gluten","poids","maigrir","grossir","mincir"]):
        ctx = score_ctx(mn, "nutrition")
        return (
            f"🥗 **Nutrition — conseils personnalisés** {ctx}\n\n"
            f"**Fondamentaux à respecter :**\n"
            f"• 🥩 Protéines à chaque repas (œufs, légumineuses, poisson, viande)\n"
            f"• 🥦 La moitié de l'assiette = légumes colorés\n"
            f"• 🫒 Bonnes graisses : avocat, huile d'olive, noix, poissons gras\n"
            f"• 🍞 Glucides complexes : riz complet, quinoa, patate douce\n"
            f"• 💧 2L d'eau/jour minimum\n"
            f"• ⏰ Évite de manger 2h avant de dormir\n\n"
            f"**À limiter :** sucre raffiné, ultra-transformés, alcool, sel en excès\n\n"
            f"💡 Astuce : la règle 80/20 — mange sainement 80% du temps, pas besoin d'être parfait !"
        )

    # Hydratation 
    if any(w in q for w in ["eau","hydratation","boire","soif","déshydraté"]):
        return (
            f"💧 **Hydratation — guide complet**\n\n"
            f"**Pourquoi c'est crucial :**\n"
            f"• Dès -1% d'hydratation → -10% de concentration\n"
            f"• Dès -2% → fatigue physique et maux de tête\n"
            f"• Le corps est composé à 60% d'eau\n\n"
            f"**Objectifs recommandés :**\n"
            f"• 💧 2.0 L/jour minimum (2.5-3L si sport ou chaleur)\n"
            f"• ☀️ +500ml par heure de sport\n"
            f"• ☕ Le café et thé comptent, mais déshydratent légèrement\n\n"
            f"**Astuce pratique :** bois un grand verre d'eau dès le réveil !"
        )

    # Café / caféine
    if any(w in q for w in ["café","caffeine","caféine","thé","energy drink","red bull","guarana"]):
        return (
            f"☕ **Caféine — ce qu'il faut savoir**\n\n"
            f"**Dose optimale :** 1 à 3 tasses/jour (200-400mg de caféine)\n\n"
            f"**Règles d'or :**\n"
            f"• ⏰ Pas de café avant 9h30 (cortisol naturellement élevé le matin)\n"
            f"• 🌙 Pas de caféine après 14h (demi-vie de 6h dans le corps)\n"
            f"• 💧 Accompagne chaque café d'un verre d'eau\n"
            f"• 🚫 +4 tasses/jour = anxiété, palpitations, insomnie\n\n"
            f"**Alternatives énergisantes :** thé matcha, eau froide, respiration Wim Hof"
        )

    # Concentration / productivité 
    if any(w in q for w in ["concentration","focus","productivité","travail","étude","mémoire","cerveau","cognitif","distraction","procrastination","pomodoro"]):
        ctx = score_ctx(mc, "concentration")
        return (
            f"🧠 **Booster ta concentration** {ctx}\n\n"
            f"**Méthodes prouvées :**\n"
            f"• ⏱️ Pomodoro : 25 min focus + 5 min pause (× 4 → 30 min pause)\n"
            f"• 📵 Téléphone hors de vue (-20% de distraction)\n"
            f"• 🎵 Musique blanche ou lo-fi (sans paroles)\n"
            f"• 🌿 Plante dans l'espace de travail (+15% productivité, étude NASA)\n"
            f"• 💧 Boire de l'eau : la déshydratation = -20% de concentration\n"
            f"• 😴 Micro-sieste 20 min après déjeuner si possible\n\n"
            f"**Aliments booster cerveau :** myrtilles, noix, sardines, œufs, avocat"
        )

    # Humeur / santé mentale 
    if any(w in q for w in ["humeur","moral","déprime","dépression","tristesse","triste","anxiété","motivation","démotivé","bien-être mental","bonheur","positif"]):
        return (
            f"😊 **Santé mentale & humeur**\n\n"
            f"**Ce qui améliore l'humeur (preuves scientifiques) :**\n"
            f"• 🏃 Exercise physique = antidépresseur naturel (libère sérotonine + dopamine)\n"
            f"• ☀️ 20 min de soleil/jour (synthèse vitamine D + sérotonine)\n"
            f"• 🤝 Connexion sociale (même courte = impact positif fort)\n"
            f"• ✍️ Gratitude (noter 3 choses positives chaque soir)\n"
            f"• 🎯 Petits objectifs atteints → dopamine\n"
            f"• 🎵 Musique que tu aimes\n\n"
            f"⚕️ Si tu ressens une tristesse persistante (+2 semaines), n'hésite pas à en parler à un professionnel — c'est normal et il y a de l'aide disponible."
        )

    # Vitamines / suppléments 
    if any(w in q for w in ["vitamine","supplément","complément","minéral","magnésium","zinc","oméga","fer","calcium","b12","d3","probiotique"]):
        return (
            f"💊 **Vitamines & suppléments — guide pratique**\n\n"
            f"**Les plus souvent déficients en Europe :**\n"
            f"• ☀️ **Vitamine D3** : 80% de la population déficiente → fatigue, immunité\n"
            f"• 🌿 **Magnésium B6** : stress, crampes, sommeil (400mg/jour)\n"
            f"• 🐟 **Oméga-3** : cerveau, inflammation, humeur\n"
            f"• 🩸 **Fer** : fatigue intense (surtout femmes) — bilan sanguin recommandé\n"
            f"• 🥩 **B12** : vital si végétarien/vegan\n\n"
            f"💡 Toujours vérifier par bilan sanguin avant de supplémenter.\n"
            f"⚕️ Consulte un médecin ou pharmacien pour un avis personnalisé."
        )

    # Poids / IMC 
    if any(w in q for w in ["poids","imc","obésité","surpoids","mincir","maigrir","grossir","masse","corps"]):
        return (
            f"⚖️ **Poids & composition corporelle**\n\n"
            f"**Approche saine :**\n"
            f"• 🎯 Objectif réaliste : -0.5 à 1 kg/semaine maximum\n"
            f"• 🍽️ Déficit calorique modéré (-300 à -500 kcal/jour)\n"
            f"• 🥩 Protéines suffisantes pour préserver le muscle\n"
            f"• 🏋️ Musculation > cardio seul pour la composition corporelle\n"
            f"• 😴 Le manque de sommeil augmente la ghréline (hormone de la faim)\n\n"
            f"**Ce qui ne marche pas :** régimes extrêmes, jeûne prolongé sans suivi, comprimés magiques\n\n"
            f"⚕️ Pour un suivi personnalisé, consulte un nutritionniste ou médecin."
        )

    # Mal de dos / posture
    if any(w in q for w in ["dos","posture","colonne","lombaire","cervicale","nuque","épaule","assis","bureau","sédentaire","douleur"]):
        return (
            f"🦴 **Posture & mal de dos — conseils pratiques**\n\n"
            f"**Au bureau :**\n"
            f"• 💺 Écran à hauteur des yeux (pas vers le bas)\n"
            f"• ⌨️ Bras à 90°, pieds à plat\n"
            f"• ⏱️ Debout ou marche 2 min toutes les 45 min\n\n"
            f"**Exercices quotidiens :**\n"
            f"• 🧘 Étirement chat-vache (dos)\n"
            f"• 💪 Planche 3×30s (renforce les abdos stabilisateurs)\n"
            f"• 🚶 Marche 30 min/jour (meilleur exercice pour le dos)\n\n"
            f"⚕️ Douleur persistante > 1 semaine = consulter un kiné ou médecin."
        )

    #  Système immunitaire 
    if any(w in q for w in ["immunitaire","immunité","tomber malade","rhume","grippe","infection","virus","défenses"]):
        return (
            f"🛡️ **Renforcer son système immunitaire**\n\n"
            f"**Les piliers :**\n"
            f"• 😴 Sommeil 7-9h — c'est pendant le sommeil que le système immunitaire travaille\n"
            f"• 🥗 Fruits et légumes colorés (vitamines C, A, E, zinc)\n"
            f"• 🏃 Exercice modéré (pas excessif → contra-productif)\n"
            f"• 💧 Bonne hydratation\n"
            f"• ☀️ Vitamine D (supplémentation en hiver recommandée)\n"
            f"• 🧘 Gestion du stress (le cortisol chronique affaiblit l'immunité)\n\n"
            f"**Ce qui affaiblit l'immunité :** tabac, alcool, manque de sommeil, stress chronique, sédentarité"
        )

    # ── Questions médicales générales ─────────────────────────────────────────
    if any(w in q for w in ["maladie","médecin","docteur","symptôme","douleur","médicament","traitement","diagnostic","consultation","urgence"]):
        return (
            f"⚕️ {prenom}, pour les questions médicales spécifiques, je te recommande toujours de consulter un **professionnel de santé**.\n\n"
            f"Je peux t'aider sur les habitudes de vie qui **préviennent** les problèmes de santé :\n"
            f"• Sommeil de qualité\n• Alimentation équilibrée\n• Activité physique régulière\n"
            f"• Gestion du stress\n• Hydratation correcte\n\n"
            f"Pour trouver un médecin : **doctolib.fr** ou ta mutuelle habituellement propose un annuaire."
        )

    # ── Félicitations / motivation ────────────────────────────────────────────
    if any(w in q for w in ["merci","bravo","super","bien","félicitation","content","fier","progrès","amélioration"]):
        return (
            f"🌟 C'est toi qui fais le travail, {prenom} — moi je suis juste là pour t'accompagner !\n\n"
            f"Ton score actuel : **{mg:.0f}/100** ({tendance})\n\n"
            f"La **régularité** est ta plus grande force. Chaque petit effort s'accumule.\n"
            f"Continue comme ça ! 💪"
        )

    # ── Réponse générique enrichie ────────────────────────────────────────────
    return (
        f"🤖 Bonjour {prenom} ! Je peux t'aider sur tous ces sujets santé :\n\n"
        f"• 🌙 **Sommeil** — insomnie, qualité, durée\n"
        f"• 😌 **Stress** — anxiété, burn-out, relaxation\n"
        f"• ⚡ **Énergie** — fatigue, vitalité, coup de pompe\n"
        f"• 🏃 **Sport** — activité physique, motivation, programme\n"
        f"• 🥗 **Nutrition** — alimentation, régime, poids\n"
        f"• 💧 **Hydratation** — eau, caféine, boissons\n"
        f"• 🧠 **Concentration** — focus, mémoire, productivité\n"
        f"• 😊 **Humeur** — moral, motivation, bien-être mental\n"
        f"• 💊 **Vitamines** — suppléments, carences\n"
        f"• 🦴 **Posture** — mal de dos, bureau, étirements\n"
        f"• 🛡️ **Immunité** — défenses, prévention\n\n"
        f"Pose ta question librement ! 😊"
    )


# ── Rapport PDF ───────────────────────────────────────────────────────────────
rapport_bp = Blueprint("rapport", __name__)

@rapport_bp.route("/rapport")
@login_required
def rapport():
    user = session["user"]
    t = get_t(session.get("lang","fr"))
    return render_template("rapport/rapport.html", user=user, t=t, current_lang=session.get("lang","fr"))

@rapport_bp.route("/rapport/generate", methods=["POST"])
@login_required
def generate():
    user    = session["user"]
    periode = int(request.form.get("periode", 30))
    email_dest       = request.form.get("email_dest", "").strip()
    sender_email     = request.form.get("sender_email", "").strip()
    sender_password  = request.form.get("sender_password", "").strip()

    historique   = db.get_historique(user["id"], limit=periode)
    statistiques = db.get_statistiques(user["id"])

    try:
        from utils.pdf_generator import PDFGenerator
        path = PDFGenerator().generer(
            user=user, historique=historique, stats=statistiques,
            inclure_graphiques=True, inclure_conseils=True, inclure_historique=True,
        )

        # Envoi email — credentials fournis directement via le formulaire
        if email_dest and sender_email and sender_password:
            from utils.email_sender import EmailSender
            EmailSender().send_with_credentials(
                dest_email=email_dest,
                sender_email=sender_email,
                sender_password=sender_password,
                pdf_path=path,
                user=user,
                stats=statistiques,
            )
            return jsonify({"success": True,
                            "message": f"✅ Rapport envoyé à {email_dest} avec succès !"})

        # Téléchargement direct sans email
        return send_file(path, as_attachment=True, download_name="rapport_sante.pdf",
                         mimetype="application/pdf")

    except Exception as e:
        return jsonify({"success": False, "message": f"❌ {str(e)}"}), 500
