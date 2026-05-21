POIDS = {
    "sommeil": 0.28,
    "stress": 0.22,
    "concentration": 0.15,
    "activite": 0.18,
    "nutrition": 0.17,
}


class ScoreCalculator:

    def _score_sommeil(self, heures: float, qualite: int) -> float:
        if 7.0 <= heures <= 9.0:
            s_duree = 100.0
        elif 6.0 <= heures < 7.0 or 9.0 < heures <= 10.0:
            s_duree = 85.0
        elif 5.0 <= heures < 6.0 or 10.0 < heures <= 11.0:
            s_duree = 65.0
        elif 4.0 <= heures < 5.0:
            s_duree = 40.0
        else:
            s_duree = 15.0

        qualite_map = {1: 25.0, 2: 55.0, 3: 80.0, 4: 100.0}
        s_qualite = qualite_map.get(int(qualite), 50.0)
        return round(s_duree * 0.60 + s_qualite * 0.40, 2)

    def _score_stress(self, niveau: int) -> float:
        stress_map = {1: 100.0, 2: 80.0, 3: 55.0, 4: 28.0, 5: 5.0}
        return stress_map.get(int(niveau), 50.0)

    def _score_concentration(self, concentration: int, humeur: int) -> float:
        s_conc = (concentration - 1) / 4 * 100
        s_humeur = (humeur - 1) / 4 * 100
        return round(s_conc * 0.65 + s_humeur * 0.35, 2)

    def _score_activite(self, minutes_sport: int, temps_ecran: float) -> float:
        if minutes_sport >= 60:
            s_sport = min(100.0, 80.0 + (minutes_sport - 60) * 0.5)
            if minutes_sport > 90:
                s_sport = max(80.0, s_sport - (minutes_sport - 90) * 0.3)
        elif 30 <= minutes_sport < 60:
            s_sport = 60.0 + (minutes_sport - 30) * 0.67
        elif 15 <= minutes_sport < 30:
            s_sport = 35.0 + (minutes_sport - 15) * 1.67
        elif 1 <= minutes_sport < 15:
            s_sport = 15.0 + minutes_sport * 1.33
        else:
            s_sport = 0.0

        if temps_ecran <= 2:
            s_ecran = 100.0
        elif temps_ecran <= 4:
            s_ecran = 100.0 - (temps_ecran - 2) * 10
        elif temps_ecran <= 8:
            s_ecran = 80.0 - (temps_ecran - 4) * 10
        else:
            s_ecran = max(0.0, 40.0 - (temps_ecran - 8) * 8)

        return round(s_sport * 0.70 + s_ecran * 0.30, 2)

    def _score_nutrition(self, cafeine: int, hydratation: float, repas_equilibre: int) -> float:
        if cafeine == 0:
            s_cafe = 90.0
        elif cafeine <= 2:
            s_cafe = 100.0
        elif cafeine <= 4:
            s_cafe = 100.0 - (cafeine - 2) * 20
        else:
            s_cafe = max(0.0, 60.0 - (cafeine - 4) * 15)

        if hydratation >= 2.0:
            s_eau = min(100.0, 70.0 + (hydratation - 2.0) * 15)
        elif hydratation >= 1.5:
            s_eau = 50.0 + (hydratation - 1.5) * 40
        elif hydratation >= 1.0:
            s_eau = 25.0 + (hydratation - 1.0) * 50
        else:
            s_eau = hydratation * 25

        s_repas = 100.0 if repas_equilibre == 1 else 30.0
        return round(s_cafe * 0.30 + s_eau * 0.40 + s_repas * 0.30, 2)

    def _penalites(self, data: dict) -> float:
        pen = 0.0
        bonus = 0.0
        if data["cafeine"] >= 4 and data["heure_sommeil"] < 6:
            pen += 0.05
        if data["niveau_stress"] >= 4 and data["sport"] == 0:
            pen += 0.04
        if data["temps_ecran"] >= 8 and data["concentration"] <= 2:
            pen += 0.03
        if data["sport"] >= 30 and data["hydratation"] >= 2.0:
            bonus += 0.03
        if data["heure_sommeil"] >= 7 and data["niveau_stress"] <= 2:
            bonus += 0.02
        return max(0.85, 1.0 - pen + bonus)

    def calculer(self, data: dict) -> dict:
        s_som = self._score_sommeil(data["heure_sommeil"], data["qualite_sommeil"])
        s_str = self._score_stress(data["niveau_stress"])
        s_con = self._score_concentration(data["concentration"], data["humeur"])
        s_act = self._score_activite(data["sport"], data["temps_ecran"])
        s_nut = self._score_nutrition(data["cafeine"], data["hydratation"], data["repas_equilibre"])

        brut = (
            s_som * POIDS["sommeil"]
            + s_str * POIDS["stress"]
            + s_con * POIDS["concentration"]
            + s_act * POIDS["activite"]
            + s_nut * POIDS["nutrition"]
        )
        score_global = round(min(100.0, max(0.0, brut * self._penalites(data))), 2)

        return {
            "score_sommeil": round(s_som, 2),
            "score_stress": round(s_str, 2),
            "score_concentration": round(s_con, 2),
            "score_activite": round(s_act, 2),
            "score_nutrition": round(s_nut, 2),
            "score_global": score_global,
            "niveau": self._niveau(score_global),
        }

    @staticmethod
    def _niveau(score: float) -> str:
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Bon"
        if score >= 50:
            return "Moyen"
        if score >= 30:
            return "Faible"
        return "Critique"

    def generer_conseils(self, data: dict, scores: dict) -> list:
        conseils = []
        if scores["score_sommeil"] < 60:
            if data["heure_sommeil"] < 7:
                conseils.append("🌙 Tu dors moins que recommandé. Vise 7 à 9h par nuit.")
            if data["qualite_sommeil"] <= 2:
                conseils.append("💤 Qualité de sommeil faible — évite les écrans 1h avant de dormir.")
        if scores["score_stress"] < 50:
            conseils.append("🧘 Stress élevé — essaie la respiration 4-7-8 ou 10 min de méditation.")
        if scores["score_activite"] < 60:
            if data["sport"] < 30:
                conseils.append("🏃 Seulement 30 min de marche rapide par jour changent tout !")
            if data["temps_ecran"] >= 8:
                conseils.append("📱 Trop d'écran — applique la règle 20-20-20 pour tes yeux.")
        if scores["score_nutrition"] < 60:
            if data["cafeine"] >= 4:
                conseils.append("☕ Trop de caféine perturbe ton sommeil et augmente l'anxiété.")
            if data["hydratation"] < 1.5:
                conseils.append("💧 Hydrate-toi mieux — 2L/jour pour une concentration optimale.")
            if data["repas_equilibre"] == 0:
                conseils.append("🥗 Améliore l'équilibre de tes repas : légumes + protéines + bonnes graisses.")
        if scores["score_concentration"] < 50:
            conseils.append("🧠 Essaie la méthode Pomodoro : 25 min de travail puis 5 min de pause.")
        if not conseils:
            conseils.append("🌟 Excellentes habitudes ! Continue comme ça, la régularité est la clé.")
        return conseils
