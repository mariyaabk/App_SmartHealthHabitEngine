"""
Tests unitaires — ScoreCalculator
Couvre les cas nominaux, limites et pénalités croisées.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.score_calculator import ScoreCalculator


@pytest.fixture
def calc():
    return ScoreCalculator()


@pytest.fixture
def bonnes_habitudes():
    """Données avec de bonnes habitudes — score attendu élevé."""
    return {
        "heure_sommeil":   8.0,
        "qualite_sommeil": 4,
        "niveau_stress":   1,
        "concentration":   5,
        "humeur":          5,
        "sport":           60,
        "temps_ecran":     2.0,
        "cafeine":         1,
        "hydratation":     2.5,
        "repas_equilibre": 1,
    }


@pytest.fixture
def mauvaises_habitudes():
    """Données avec de mauvaises habitudes — score attendu faible."""
    return {
        "heure_sommeil":   3.0,
        "qualite_sommeil": 1,
        "niveau_stress":   5,
        "concentration":   1,
        "humeur":          1,
        "sport":           0,
        "temps_ecran":     12.0,
        "cafeine":         8,
        "hydratation":     0.5,
        "repas_equilibre": 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS SCORE SOMMEIL
# ─────────────────────────────────────────────────────────────────────────────
class TestScoreSommeil:

    def test_sommeil_optimal(self, calc):
        """7 à 9h de sommeil + excellente qualité → score maximal."""
        score = calc._score_sommeil(8.0, 4)
        assert score == 100.0

    def test_sommeil_court(self, calc):
        """Moins de 4h → score très faible."""
        score = calc._score_sommeil(3.0, 1)
        assert score < 30

    def test_sommeil_trop_long(self, calc):
        """Plus de 10h → score réduit."""
        score = calc._score_sommeil(11.5, 3)
        assert score < 70

    def test_sommeil_limite_basse(self, calc):
        """6h (limite basse acceptable) → score moyen."""
        score = calc._score_sommeil(6.0, 3)
        assert 50 <= score <= 85

    def test_sommeil_qualite_mauvaise(self, calc):
        """Bonne durée mais mauvaise qualité → score pénalisé."""
        score_bonne  = calc._score_sommeil(8.0, 4)
        score_mauvaise = calc._score_sommeil(8.0, 1)
        assert score_bonne > score_mauvaise


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS SCORE STRESS
# ─────────────────────────────────────────────────────────────────────────────
class TestScoreStress:

    def test_stress_tres_bas(self, calc):
        assert calc._score_stress(1) == 100.0

    def test_stress_tres_eleve(self, calc):
        assert calc._score_stress(5) == 5.0

    def test_stress_modere(self, calc):
        score = calc._score_stress(3)
        assert score == 55.0

    def test_stress_inverse(self, calc):
        """Plus le stress est élevé, plus le score est bas."""
        scores = [calc._score_stress(i) for i in range(1, 6)]
        assert scores == sorted(scores, reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS SCORE ACTIVITÉ
# ─────────────────────────────────────────────────────────────────────────────
class TestScoreActivite:

    def test_aucune_activite(self, calc):
        score = calc._score_activite(0, 4.0)
        assert score < 30

    def test_activite_optimale(self, calc):
        score = calc._score_activite(60, 2.0)
        assert score >= 80

    def test_trop_ecran_penalise(self, calc):
        score_peu  = calc._score_activite(30, 2.0)
        score_bcp  = calc._score_activite(30, 10.0)
        assert score_peu > score_bcp

    def test_activite_minimale_oms(self, calc):
        """30 min (recommandation OMS) → score acceptable."""
        score = calc._score_activite(30, 4.0)
        assert score >= 50


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS SCORE NUTRITION
# ─────────────────────────────────────────────────────────────────────────────
class TestScoreNutrition:

    def test_nutrition_parfaite(self, calc):
        score = calc._score_nutrition(1, 2.5, 1)
        assert score >= 85

    def test_trop_cafeine(self, calc):
        score_ok  = calc._score_nutrition(2, 2.0, 1)
        score_bcp = calc._score_nutrition(8, 2.0, 1)
        assert score_ok > score_bcp

    def test_mauvaise_hydratation(self, calc):
        score_ok  = calc._score_nutrition(2, 2.0, 1)
        score_bad = calc._score_nutrition(2, 0.5, 1)
        assert score_ok > score_bad

    def test_repas_non_equilibre(self, calc):
        score_eq  = calc._score_nutrition(2, 2.0, 1)
        score_neq = calc._score_nutrition(2, 2.0, 0)
        assert score_eq > score_neq


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS SCORE GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
class TestScoreGlobal:

    def test_bonnes_habitudes_score_eleve(self, calc, bonnes_habitudes):
        result = calc.calculer(bonnes_habitudes)
        assert result["score_global"] >= 75
        assert result["niveau"] in ["Excellent", "Bon"]

    def test_mauvaises_habitudes_score_faible(self, calc, mauvaises_habitudes):
        result = calc.calculer(mauvaises_habitudes)
        assert result["score_global"] <= 40
        assert result["niveau"] in ["Faible", "Critique", "Moyen"]

    def test_score_entre_0_et_100(self, calc, bonnes_habitudes, mauvaises_habitudes):
        for data in [bonnes_habitudes, mauvaises_habitudes]:
            result = calc.calculer(data)
            assert 0 <= result["score_global"] <= 100

    def test_toutes_cles_presentes(self, calc, bonnes_habitudes):
        result = calc.calculer(bonnes_habitudes)
        cles_attendues = [
            "score_sommeil", "score_stress", "score_concentration",
            "score_activite", "score_nutrition", "score_global", "niveau"
        ]
        for cle in cles_attendues:
            assert cle in result

    def test_penalite_cafe_sommeil(self, calc):
        """Beaucoup de café + peu de sommeil → pénalité appliquée."""
        data_normal = {
            "heure_sommeil": 8.0, "qualite_sommeil": 3, "niveau_stress": 2,
            "concentration": 4, "humeur": 4, "sport": 30, "temps_ecran": 3.0,
            "cafeine": 1, "hydratation": 2.0, "repas_equilibre": 1,
        }
        data_penalise = {**data_normal, "cafeine": 6, "heure_sommeil": 4.0}
        score_n = calc.calculer(data_normal)["score_global"]
        score_p = calc.calculer(data_penalise)["score_global"]
        assert score_n > score_p


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS NIVEAUX
# ─────────────────────────────────────────────────────────────────────────────
class TestNiveaux:

    @pytest.mark.parametrize("score,niveau_attendu", [
        (90, "Excellent"),
        (75, "Bon"),
        (55, "Moyen"),
        (35, "Faible"),
        (20, "Critique"),
    ])
    def test_niveaux(self, score, niveau_attendu):
        assert ScoreCalculator._niveau(score) == niveau_attendu


# ─────────────────────────────────────────────────────────────────────────────
#  TESTS CONSEILS
# ─────────────────────────────────────────────────────────────────────────────
class TestConseils:

    def test_conseils_non_vide(self, calc, mauvaises_habitudes):
        scores = calc.calculer(mauvaises_habitudes)
        conseils = calc.generer_conseils(mauvaises_habitudes, scores)
        assert len(conseils) > 0

    def test_conseils_bonnes_habitudes(self, calc, bonnes_habitudes):
        scores = calc.calculer(bonnes_habitudes)
        conseils = calc.generer_conseils(bonnes_habitudes, scores)
        # Avec de bonnes habitudes, message positif attendu
        assert any("🌟" in c or "Continue" in c or "Excellent" in c for c in conseils)

    def test_conseil_sommeil_insuffisant(self, calc):
        data = {
            "heure_sommeil": 4.0, "qualite_sommeil": 1, "niveau_stress": 3,
            "concentration": 3, "humeur": 3, "sport": 30, "temps_ecran": 4.0,
            "cafeine": 2, "hydratation": 2.0, "repas_equilibre": 1,
        }
        scores = calc.calculer(data)
        conseils = calc.generer_conseils(data, scores)
        assert any("sommeil" in c.lower() or "dormir" in c.lower() or "🌙" in c for c in conseils)
