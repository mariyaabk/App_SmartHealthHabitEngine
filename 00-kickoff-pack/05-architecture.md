
## 05 — Architecture

### 1. Schéma de composants

```
┌─────────────────────────────────────────────────────┐
│           NAVIGATEUR (HTML + Tailwind CSS)          │
│     Chart.js · i18n.js · Notifications API          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP (port 5000)
┌────────────────────▼────────────────────────────────┐
│          FLASK — COUCHE ROUTES (routes/)            │
│   auth · dashboard · questionnaire · stats · ai    │
└─────────┬───────────────────────────┬───────────────┘
          │                           │
┌─────────▼──────────┐  ┌────────────▼────────────────┐
│  LOGIQUE MÉTIER    │  │  ACCÈS DONNÉES              │
│  models/           │  │  database/db_manager.py     │
│  score_calculator  │  │  Requêtes préparées SQL     │
│  patterns/         │  └────────────┬────────────────┘
│  pdf_generator     │               │
└────────────────────┘  ┌────────────▼────────────────┐
                        │  MySQL — smart_health_db    │
                        │  utilisateurs · habitudes   │
                        │  scores · conversations_ia  │
                        └─────────────────────────────┘
```

### 2. Séparation des couches

| Couche | Fichiers | Responsabilité |
|---|---|---|
| Routes (API) | `routes/*.py` | Reçoit les requêtes HTTP, vérifie la session, retourne les templates Jinja2 |
| Logique métier | `models/score_calculator.py` `patterns/design_patterns.py` | Calcul des scores pondérés, design patterns, génération PDF |
| Accès données | `database/db_manager.py` | Toutes les requêtes SQL (requêtes préparées), CRUD complet |

### 3. Design Patterns implémentés

| Pattern | Fichier | Rôle |
|---|---|---|
| **Singleton** | `database/db_manager.py` | Une seule instance de connexion MySQL dans toute l'app |
| **Factory** | `patterns/design_patterns.py` → `ScoreCalculatorFactory` | Création flexible des calculateurs selon le profil |
| **Observer** | `patterns/design_patterns.py` → `QuestionnaireService` | Alerte automatique si score critique (< 30/100) |
| **Strategy** | `patterns/design_patterns.py` → `ScoringContext` | Algorithme de scoring interchangeable (pondéré / simple) |

### 4. Sécurité by design

| Réflexe | Statut | Détail |
|---|---|---|
| HTTPS | ❌ (localhost dev) | Non configuré — MVP local uniquement |
| Secrets en variables d'env | ✅ Partiel | `settings.py` avec `os.environ` — docker-compose injecte les vars |
| Mots de passe hachés | ✅ | SHA-256 + salt (dette : migrer vers bcrypt en V1.1) |
| Sessions sécurisées | ✅ | Flask sessions côté serveur avec `SECRET_KEY` |
| Protection injection SQL | ✅ | Requêtes préparées avec paramètres `%s` |
| Rate limiting /login | ❌ | Non implémenté — dette acceptée |
| RGPD | ⚠️ Partiel | Suppression compte implémentée, pas de durée de rétention définie |
| Audit log | ❌ | Non implémenté — dette acceptée |

### 5. Observabilité minimale

- **Logs** : `print()` Flask natif — logs Docker accessibles via `docker-compose logs`
- **Service rappel** : logs préfixés `[ReminderService]` en console
- **Métriques** : non implémentées — prévu V2
- **Traces** : non implémentées — prévu V2

---