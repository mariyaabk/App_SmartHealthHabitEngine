## 06 — Architecture Decision Records

### ADR-001 — Choix de la base de données : MySQL

| Champ | Valeur |
|---|---|
| Date | 2025-04-01 |
| Statut | ✅ Accepté |
| Décideur | Mariya ABAAKIL |

**Contexte** : Besoin de stocker des données structurées et relationnelles : utilisateurs, habitudes quotidiennes et scores calculés. Données fortement liées (jointures nécessaires).

**Options envisagées** : MySQL 8.0 · SQLite · MongoDB

**Décision** : MySQL 8.0 via `mysql-connector-python`

**Justification** :
- Données fortement relationnelles → SQL naturellement adapté
- Visualisable via MySQL Workbench pendant le développement
- Équipe maîtrise SQL — pas de surcoût d'apprentissage
- Jointures nécessaires entre utilisateurs, habitudes et scores

**Conséquences** :
- ✅ Requêtes analytiques simples (moyennes, historique)
- ✅ Intégrité référentielle garantie par les FK
- ⚠️ Gestion manuelle des migrations (pas d'ORM)

---

### ADR-002 — Choix du framework backend : Flask

| Champ | Valeur |
|---|---|
| Date | 2025-04-01 |
| Statut | ✅ Accepté |
| Décideur | Mariya ABAAKIL |

**Contexte** : Besoin d'un framework Python pour servir des routes HTTP, des templates HTML et une API simple. Projet solo avec délai court.

**Options envisagées** : Flask · Django · FastAPI

**Décision** : Flask 3.0

**Justification** :
- Plus léger et suffisant pour ce scope (pas besoin d'ORM intégré, admin, etc.)
- Technologie maîtrisée — pas de surcoût d'apprentissage
- Démarrage rapide compatible avec le délai MVP
- Flexibilité pour choisir les composants (MySQL direct, Jinja2, etc.)

**Conséquences** :
- ✅ Rapidité de développement
- ✅ Contrôle total sur l'architecture
- ⚠️ Pas d'ORM — requêtes SQL manuelles (requêtes préparées obligatoires)

---

### ADR-003 — Choix de conteneurisation : Docker

| Champ | Valeur |
|---|---|
| Date | 2025-04-15 |
| Statut | ✅ Accepté |
| Décideur | Mariya ABAAKIL |

**Contexte** : Besoin de garantir la reproductibilité du projet sur n'importe quelle machine. Deux dépendances système : Python 3.11 et MySQL 8.0.

**Options envisagées** : Docker + docker-compose · Déploiement manuel · PaaS (Heroku, Railway)

**Décision** : Docker + docker-compose avec deux services : `shhe_app` (Flask) + `shhe_db` (MySQL)

**Justification** :
- `git clone` + `docker-compose up` = projet fonctionnel en < 5 minutes
- Isole Flask et MySQL dans des conteneurs séparés
- Pas de dépendance à l'environnement local du correcteur
- Compatible avec le pipeline CI/CD GitHub Actions

**Conséquences** :
- ✅ Reproductibilité garantie sur toute machine
- ✅ MySQL géré automatiquement — pas de configuration locale
- ⚠️ Décalage timezone UTC/locale à gérer (`TZ=Europe/Paris` dans docker-compose)

---