"""
Design Patterns — SHHE
  Pattern 1 : Singleton  -> DatabaseManager
  Pattern 2 : Factory    -> ScoreCalculatorFactory
  Pattern 3 : Observer   -> QuestionnaireService
  Pattern 4 : Strategy   -> ScoringContext
"""

from abc import ABC, abstractmethod
from typing import List
from models.score_calculator import ScoreCalculator


# ======================================================================
#  PATTERN 1 — SINGLETON
# ======================================================================
class SingletonMeta(type):
    """Metaclasse Singleton — une seule instance par classe."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# ======================================================================
#  PATTERN 2 — FACTORY
# ======================================================================
class ScoreCalculatorFactory:
    """Factory pour creer des calculateurs de score."""

    @staticmethod
    def create(calculator_type: str = "standard") -> ScoreCalculator:
        calculators = {
            "standard": ScoreCalculator,
        }
        cls = calculators.get(calculator_type, ScoreCalculator)
        return cls()


# ======================================================================
#  PATTERN 3 — OBSERVER
# ======================================================================
class Observer(ABC):
    """Interface Observer."""

    @abstractmethod
    def update(self, event: str, data: dict):
        pass


class Subject:
    """Sujet observable."""

    def __init__(self):
        self._observers: List[Observer] = []

    def subscribe(self, observer: Observer):
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, event: str, data: dict):
        for observer in self._observers:
            observer.update(event, data)


class ScoreAlertObserver(Observer):
    """Alerte si le score global est critique (< 30)."""

    def update(self, event: str, data: dict):
        if event == "questionnaire_submitted":
            score = data.get("score_global", 0)
            if score < 30:
                print(f"ALERTE : Score critique ({score}/100) user {data.get('user_id')}")


class StreakObserver(Observer):
    """Suit la regularite de l'utilisateur."""

    def update(self, event: str, data: dict):
        if event == "questionnaire_submitted":
            user_id = data.get("user_id")
            print(f"Streak mis a jour pour l'utilisateur {user_id}")


class QuestionnaireService(Subject):
    """Service principal du questionnaire."""

    def __init__(self):
        super().__init__()
        self.subscribe(ScoreAlertObserver())
        self.subscribe(StreakObserver())

    def submit(self, user_id: int, scores: dict):
        data = {"user_id": user_id, **scores}
        self.notify("questionnaire_submitted", data)
        return data


# ======================================================================
#  PATTERN 4 — STRATEGY
# ======================================================================
class ScoringStrategy(ABC):
    """Interface Strategy."""

    @abstractmethod
    def calculate(self, data: dict) -> float:
        pass


class WeightedScoringStrategy(ScoringStrategy):
    """Strategie ponderee — algorithme actuel de SHHE."""

    def calculate(self, data: dict) -> float:
        calc = ScoreCalculator()
        scores = calc.calculer(data)
        return scores["score_global"]


class SimpleScoringStrategy(ScoringStrategy):
    """Strategie simplifiee — moyenne simple."""

    def calculate(self, data: dict) -> float:
        calc = ScoreCalculator()
        scores = calc.calculer(data)
        vals = [
            scores["score_sommeil"],
            scores["score_stress"],
            scores["score_concentration"],
            scores["score_activite"],
            scores["score_nutrition"],
        ]
        return round(sum(vals) / len(vals), 2)


class ScoringContext:
    """Contexte Strategy — utilise la strategie injectee."""

    def __init__(self, strategy: ScoringStrategy = None):
        self._strategy = strategy or WeightedScoringStrategy()

    def set_strategy(self, strategy: ScoringStrategy):
        self._strategy = strategy

    def compute_score(self, data: dict) -> float:
        return self._strategy.calculate(data)
