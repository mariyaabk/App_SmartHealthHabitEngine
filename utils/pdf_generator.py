"""PDF Generator pour le rapport SHHE (Flask version)."""
import os, datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, Image as RLImage, PageBreak)
from reportlab.lib.enums import TA_CENTER
from models.score_calculator import ScoreCalculator


class PDFGenerator:
    BLEU  = colors.HexColor("#0288d1")
    VERT  = colors.HexColor("#00897b")
    GRIS_C = colors.HexColor("#f8fafc")
    BLANC  = colors.white

    def generer(self, user, historique, stats, **kwargs) -> str:
        out = os.path.join(os.path.expanduser("~"), "SmartHealthReports")
        os.makedirs(out, exist_ok=True)
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out, f"rapport_{user.get('prenom','')}_{now}.pdf")

        doc = SimpleDocTemplate(path, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

        s = {
            "h1": ParagraphStyle("h1", fontSize=26, textColor=self.BLEU, alignment=TA_CENTER, spaceAfter=6, fontName="Helvetica-Bold"),
            "h2": ParagraphStyle("h2", fontSize=15, textColor=self.BLEU, spaceBefore=10, spaceAfter=5, fontName="Helvetica-Bold"),
            "body": ParagraphStyle("body", fontSize=11, spaceAfter=4, leading=16),
            "small": ParagraphStyle("small", fontSize=9, textColor=colors.grey),
        }

        story = [
            Spacer(1, 1.5*cm),
            Paragraph("🧠 Smart Health Habit Engine", s["h1"]),
            Paragraph(f"Rapport de bien-être — {user.get('prenom','')} {user.get('nom','')}", s["small"]),
            Paragraph(f"Généré le {datetime.date.today().strftime('%d/%m/%Y')}", s["small"]),
            HRFlowable(width="100%", thickness=2, color=self.BLEU, spaceAfter=20),
            Spacer(1, 0.5*cm),
            Paragraph("📊 Scores moyens", s["h2"]),
        ]

        # Table scores
        data = [["Dimension","Score moyen","Niveau"]] + [
            [lbl, f"{stats.get(key) or 0:.1f}/100", self._niv(stats.get(key) or 0)]
            for lbl, key in [
                ("🌙 Sommeil","moy_sommeil"),("😌 Anti-stress","moy_stress"),
                ("🧠 Concentration","moy_concentration"),("🏃 Activité","moy_activite"),
                ("🥗 Nutrition","moy_nutrition"),("⭐ GLOBAL","moyenne_globale"),
            ]
        ]
        t = Table(data, colWidths=[7*cm,5*cm,5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),self.BLEU),("TEXTCOLOR",(0,0),(-1,0),self.BLANC),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),11),
            ("ROWBACKGROUNDS",(0,1),(-1,-2),[self.GRIS_C,colors.white]),
            ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#e3f2fd")),
            ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.5,colors.lightgrey),
            ("PADDING",(0,0),(-1,-1),8),("ALIGN",(1,0),(-1,-1),"CENTER"),
        ]))
        story.append(t)

        # Graphique
        if historique and kwargs.get("inclure_graphiques", True):
            story.append(PageBreak())
            story.append(Paragraph("📈 Évolution", s["h2"]))
            img = self._make_chart(historique)
            if img:
                story.append(img)

        # Conseils
        if historique and kwargs.get("inclure_conseils", True):
            story.append(Paragraph("💡 Conseils", s["h2"]))
            calc = ScoreCalculator()
            last = historique[0]
            data_c = {k: float(last.get(k,0)) if k in ("heure_sommeil","temps_ecran","hydratation")
                      else int(last.get(k,0)) for k in
                      ["heure_sommeil","qualite_sommeil","niveau_stress","concentration",
                       "humeur","sport","temps_ecran","cafeine","hydratation","repas_equilibre"]}
            sc = {k: float(last.get(k,70)) for k in
                  ["score_sommeil","score_stress","score_concentration","score_activite","score_nutrition"]}
            for c in calc.generer_conseils(data_c, sc):
                story.append(Paragraph(f"• {c}", s["body"]))

        doc.build(story)
        return path

    def _make_chart(self, historique):
        hist = list(reversed(historique))
        dates = [r["date_score"] for r in hist]
        g = [r["score_global"] for r in hist]
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(dates, g, color="#0288d1", linewidth=2, marker="o", markersize=4)
        ax.fill_between(range(len(dates)), g, alpha=0.1, color="#0288d1")
        ax.set_xticks(range(len(dates))); ax.set_xticklabels(dates, rotation=45, ha="right", fontsize=8)
        ax.set_ylim(0, 100); ax.set_title("Score global de bien-être", fontsize=12)
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig); buf.seek(0)
        return RLImage(buf, width=15*cm, height=6*cm)

    @staticmethod
    def _niv(s):
        if s >= 85: return "✅ Excellent"
        if s >= 70: return "👍 Bon"
        if s >= 50: return "⚠️ Moyen"
        if s >= 30: return "❌ Faible"
        return "🚨 Critique"
