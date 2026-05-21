"""
Tests unitaires — Design Patterns
"""

import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from patterns.design_patterns import (
    ScoreCalculatorFactory, QuestionnaireService,
    ScoringContext, WeightedScoringStrategy, SimpleScoringStrategy
)


@pytest.fixture
def sample_data():
    return {
        "heure_sommeil": 7.0, "qualite_sommeil": 3,
        "niveau_stress": 2, "concentration": 4, "humeur": 4,
        "sport": 30, "temps_ecran": 3.0,
        "cafeine": 2, "hydratation": 2.0, "repas_equilibre": 1,
    }


class TestFactory:
    def test_factory_retourne_calculator(self, sample_data):
        calc = ScoreCalculatorFactory.create("standard")
        result = calc.calculer(sample_data)
        assert "score_global" in result

    def test_factory_type_inconnu_fallback(self, sample_data):
        calc = ScoreCalculatorFactory.create("inconnu")
        result = calc.calculer(sample_data)
        assert result["score_global"] >= 0


class TestObserver:
    def test_questionnaire_service_notifie(self, sample_data):
        service = QuestionnaireService()
        result = service.submit(user_id=1, scores={"score_global": 75})
        assert result["user_id"] == 1
        assert result["score_global"] == 75

    def test_alerte_score_critique(self, capsys, sample_data):
        service = QuestionnaireService()
        service.submit(user_id=1, scores={"score_global": 20})
        captured = capsys.readouterr()
        assert "ALERTE" in captured.out or "critique" in captured.out.lower()


class TestStrategy:
    def test_weighted_strategy(self, sample_data):
        ctx = ScoringContext(WeightedScoringStrategy())
        score = ctx.compute_score(sample_data)
        assert 0 <= score <= 100

    def test_simple_strategy(self, sample_data):
        ctx = ScoringContext(SimpleScoringStrategy())
        score = ctx.compute_score(sample_data)
        assert 0 <= score <= 100

    def test_changement_strategy(self, sample_data):
        ctx = ScoringContext(WeightedScoringStrategy())
        score1 = ctx.compute_score(sample_data)
        ctx.set_strategy(SimpleScoringStrategy())
        score2 = ctx.compute_score(sample_data)
        # Les deux scores sont valides même s'ils diffèrent
        assert 0 <= score1 <= 100
        assert 0 <= score2 <= 100
