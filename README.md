# 🧠 Smart Health Habit Engine

> Application web de suivi des habitudes de santé quotidiennes avec scores personnalisés, dashboard interactif, assistant IA et génération de rapports PDF.

-----

## 📋 Table des matières

- [Présentation](#présentation)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation & Lancement](#installation--lancement)
  - [Mode local (développement)](#mode-local-développement)
  - [Mode Docker](#mode-docker)
- [Configuration settings.py](#configuration-settingspy)
- [Lancer les tests](#lancer-les-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Structure du projet](#structure-du-projet)
- [Fonctionnalités](#fonctionnalités)
- [Base de données](#base-de-données)

-----

## Présentation

**Smart Health Habit Engine** aide les utilisateurs à suivre leurs habitudes quotidiennes (sommeil, stress, sport, nutrition…) et à améliorer leur bien-être grâce à des scores calculés automatiquement et des recommandations personnalisées.

**Utilisateur cible :** toute personne souhaitant prendre soin de sa santé au quotidien, via une interface web simple accessible depuis n’importe quel navigateur.

-----

## Stack technique

|Technologie        |Usage                 |
|-------------------|----------------------|
|Python 3.11 + Flask|Backend & routes      |
|MySQL 8.0          |Base de données       |
|Tailwind CSS       |Interface utilisateur |
|Chart.js           |Graphiques interactifs|
|ReportLab          |Génération PDF        |
|Docker + Compose   |Conteneurisation      |
|GitHub Actions     |CI/CD pipeline        |
|pytest             |Tests unitaires       |
|flake8             |Qualité du code       |

-----

## Prérequis

### Mode local

- Python 3.10+
- MySQL Server (MySQL Workbench recommandé)
- pip

### Mode Docker

- Docker Desktop installé et démarré
- Aucune autre installation requise

-----

## Installation & Lancement 

**Étape 1 — Configurer la base de données**

Ouvre `config/settings.py` et modifie le mot de passe MySQL :

```python
DB_CONFIG = {
    "host":     "localhost",
    "password": "TON_MOT_DE_PASSE_MYSQL",   # ← modifier ici
    ...
}
```

**Étape 2 — Vérifier que MySQL est démarré**

- Ouvre MySQL Workbench et vérifie que le serveur tourne
- Ou via les services Windows : MySQL → Démarrer

### Mode Docker

> ⚠️ Docker Desktop doit être installé et démarré (icône verte dans la barre des tâches).

**Étape 1 — Cloner le projet**

```bash
git clone https://github.com/mariyaabk/App_SmartHealthHabitEngine.git
cd SmartHealthHabitEngine
```

**Étape 2 — Lancer tout en une commande**

```bash
docker-compose up --build
```

Docker va automatiquement :

- Construire l’image Python 3.11
- Démarrer un conteneur MySQL
- Installer toutes les dépendances
- Lancer l’application Flask

**Étape 3 — Ouvrir dans le navigateur**

```
http://localhost:5000
```

**Arrêter l’application**

```bash
docker-compose down
```
**Lancer l’application après la configuration initiale**
```bash
docker-compose up
```
-----

### Variables d’environnement (Docker)

Sous Docker, les valeurs sont injectées automatiquement via `docker-compose.yml`.
Tu peux aussi créer un fichier `.env` (copie `.env.example`) :

```bash
cp .env.example .env
# Modifier les valeurs dans .env
```

-----

## Lancer les tests

### Tests unitaires (sans base de données)

```bash
# Installer pytest si pas encore fait
pip install pytest pytest-cov

# Lancer les tests unitaires et les tests de patterns
pytest tests/test_score_calculator.py tests/test_patterns.py -v
```
Ou 
```bash
python -m pytest tests/test_score_calculator.py tests/test_patterns.py -v                                                   
```
**Ce qui est testé :**

|Fichier                   |Ce qu’il teste                                                                                         |
|--------------------------|-------------------------------------------------------------------------------------------------------|
|`test_score_calculator.py`|Algorithme de calcul des scores (sommeil, stress, activité, nutrition, score global, niveaux, conseils)|
|`test_patterns.py`        |Design patterns (Factory, Observer, Strategy)                                                          |
|`test_routes.py`          |Routes Flask (login, register, routes protégées) — nécessite une BDD                                   |

### Avec rapport de couverture

```bash
pytest tests/test_score_calculator.py tests/test_patterns.py -v \
  --cov=models --cov=patterns --cov-report=term-missing
```

Ou
```bash
python -m pytest tests/test_score_calculator.py tests/test_patterns.py -v --cov=models --cov=patterns --cov-report=term-missing
```

### Tester les routes Flask (nécessite MySQL démarré)

```bash
pytest tests/test_routes.py -v
```
Ou
```bash
python -m pytest tests/test_routes.py -v
```

### Lancer tous les tests

```bash
pytest tests/ -v
```
Ou
```bash
python -m pytest tests/ -v      
```
### Lancer le linter (qualité du code)
### Si flake8 n’est pas installé, installe-le d’abord
```bash
pip install flake8
```

# Vérification erreurs critiques uniquement
```bash
flake8 models/ patterns/ --select=E9,F63,F7,F82 --show-source
```
Ou
```bash
python -m flake8 models/ patterns/ --select=E9,F63,F7,F82 --show-source
```                
# Vérification du style complet
```bash
flake8 models/ patterns/ --max-line-length=120 --statistics
```
Ou
```bash
python -m flake8 models/ patterns/ --max-line-length=120 --statistics                   
```
-----

## CI/CD Pipeline

Le pipeline GitHub Actions se déclenche **automatiquement** à chaque `git push`.

**Pour voir le pipeline :**

1. Va sur ton repo GitHub
1. Clique sur l’onglet **Actions**
1. Clique sur le dernier workflow

**Les 3 jobs du pipeline :**

|Job              |Durée|Ce qu’il fait                              |
|-----------------|-----|-------------------------------------------|
|🧪 Tests unitaires|~30s |Lance pytest + rapport de couverture       |
|🔍 Qualité du code|~10s |Lance flake8                               |
|🐳 Build Docker   |~35s |Construit l’image Docker (si tests passent)|

**Pour déclencher manuellement :**

```bash
git add .
git commit -m "feat: ma modification"
git push
# → pipeline se lance automatiquement sur GitHub Actions
```

-----

## Structure du projet

```
SmartHealthHabitEngine/
│
├── app.py                          # Point d'entrée Flask
├── reset_db.py                     # Réinitialiser les tables BDD
├── requirements.txt                # Dépendances Python
├── pytest.ini                      # Configuration pytest
├── Dockerfile                      # Image Docker
├── docker-compose.yml              # Orchestration Flask + MySQL
├── .env.example                    # Template variables d'environnement
├── .gitignore
│
├── config/
│   └── settings.py                 # Configuration globale (BDD, email, OpenAI)
│
├── database/
│   └── db_manager.py               # Toutes les opérations MySQL (CRUD)
│
├── models/
│   └── score_calculator.py         # Algorithme de calcul des scores (logique métier)
│
├── patterns/
│   └── design_patterns.py          # Singleton, Factory, Observer, Strategy
│
├── routes/
│   ├── auth_routes.py              # Inscription, connexion, déconnexion
│   ├── dashboard_routes.py         # Page d'accueil après connexion
│   ├── questionnaire_routes.py     # Questionnaire (1 question à la fois)
│   ├── stats_routes.py             # Statistiques + graphiques + IA + rapport
│   ├── calendar_routes.py          # Calendrier santé
│   ├── ai_routes.py                # Assistant IA
│   ├── rapport_routes.py           # Génération PDF + email
│   └── settings_routes.py          # Page paramètres
│
├── templates/                      # Pages HTML (Jinja2 + Tailwind CSS)
│   ├── base.html                   # Layout commun (sidebar, notifications, i18n)
│   ├── auth/                       # Login + register
│   ├── dashboard/                  # Accueil
│   ├── questionnaire/              # Questions + résultats
│   ├── stats/                      # Statistiques + graphiques
│   ├── calendar/                   # Calendrier santé
│   ├── ai/                         # Assistant IA chatbot
│   ├── rapport/                    # Génération PDF
│   └── settings/                   # Paramètres langue + notifications
│
├── static/
│   └── js/
│       └── i18n.js                 # Traductions FR / EN (toutes les pages)
│
├── utils/
│   ├── pdf_generator.py            # Génération rapport PDF (ReportLab)
│   ├── email_sender.py             # Envoi email SMTP Gmail
│   └── reminder.py                 # Rappels automatiques
│
├── tests/
│   ├── test_score_calculator.py    # Tests unitaires scores (20+ tests)
│   ├── test_routes.py              # Tests routes Flask
│   └── test_patterns.py            # Tests design patterns
│
└── .github/
    └── workflows/
        └── ci.yml                  # Pipeline CI/CD GitHub Actions
```

-----

## Fonctionnalités

|Fonctionnalité    |Description                                                     |
|------------------|----------------------------------------------------------------|
|🔐 Authentification|Inscription / Connexion / Déconnexion (SHA-256 + sessions Flask)|
|📋 Questionnaire   |10 questions affichées une par une avec barre de progression    |
|📊 Dashboard       |Statistiques et graphiques Chart.js interactifs                 |
|📅 Calendrier santé|Visualisation mensuelle colorée selon les scores                |
|🤖 Assistant IA    |Chatbot santé (moteur de règles + OpenAI optionnel)             |
|📄 Rapport PDF     |Export complet avec graphiques, scores et conseils              |
|📧 Email           |Envoi du rapport via Gmail (App Password)                       |
|🔔 Notifications   |Rappels quotidiens via l’API Notifications du navigateur        |
|🌍 Traduction      |Interface complète FR / EN (toutes les pages)                   |
|🎨 Design Patterns |Singleton, Factory, Observer, Strategy                          |

-----

## Base de données

### Tables créées automatiquement

|Table             |Contenu                                    |
|------------------|-------------------------------------------|
|`utilisateurs`    |Comptes avec mots de passe hashés SHA-256  |
|`habitudes`       |Réponses brutes du questionnaire           |
|`scores`          |Scores calculés par dimension et global    |
|`conversations_ia`|Historique des échanges avec l’assistant IA|
|`rappels`         |Configuration des rappels                  |

### Voir les tables dans MySQL Workbench

1. Ouvrir MySQL Workbench
1. Se connecter au serveur local
1. Schemas → `smart_health_db` → Tables
1. Clic droit → **Select Rows**

### Requêtes utiles

```sql
-- Tous les scores d'un utilisateur
SELECT u.prenom, s.date_score, s.score_global, s.niveau
FROM scores s JOIN utilisateurs u ON s.utilisateur_id = u.id
ORDER BY s.date_score DESC;

-- Moyennes par utilisateur
SELECT u.prenom, ROUND(AVG(s.score_global),1) AS moyenne, COUNT(*) AS jours
FROM scores s JOIN utilisateurs u ON s.utilisateur_id = u.id
GROUP BY u.id;
```

### Réinitialiser la base de données

En cas d’erreur de schéma :

```bash
python reset_db.py
# Taper "oui" pour confirmer
```

> ⚠️ Cela supprime toutes les données existantes.

-----

## App Password Gmail (pour l’envoi d’email)

1. Aller sur **myaccount.google.com** → Sécurité
1. Activer la **Validation en 2 étapes**
1. Cliquer sur **Mots de passe des applications**
1. Taper un nom (ex: SHHE) → **Créer**
1. Copier les **16 caractères** générés → les coller dans l’interface SHHE

-----

*Smart Health Habit Engine — Mariya ABAAKIL — 2025/2026*
