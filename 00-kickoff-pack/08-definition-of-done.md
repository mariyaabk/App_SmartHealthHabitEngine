## 08 — Definition of Done

### Cadrage
- [x] Brief 1 page rédigé
- [x] Problème, cible, contexte, contraintes formalisés

### Périmètre
- [x] User stories rédigées et priorisées en MoSCoW
- [x] MVP défini avec liste IN/OUT explicite

### Modèle métier
- [x] Rôles RBAC définis (1 rôle au MVP)
- [x] Règles métier numérotées (RM-01 à RM-06)
- [x] Machine à états du questionnaire documentée
- [x] Cas d'erreur identifiés

### Base de données
- [x] ERD validé — 5 tables avec relations
- [x] Dictionnaire de données rédigé
- [x] Contraintes d'intégrité (FK, UNIQUE)
- [ ] Soft delete *(dette acceptée — V2)*
- [ ] Timestamps `updated_at` sur toutes les tables *(dette acceptée — V2)*

### Architecture
- [x] Schéma de composants validé (3 couches)
- [x] Séparation routes / logique métier / accès données
- [x] 4 Design Patterns implémentés et testés
- [x] Réflexes sécurité partiellement validés (5/8)
- [x] Observabilité minimale (logs console Docker)

### ADR
- [x] ADR-001 : Choix MySQL
- [x] ADR-002 : Choix Flask
- [x] ADR-003 : Choix Docker

### CI/CD & Tests
- [x] Pipeline GitHub Actions opérationnel (3 jobs verts ✅)
- [x] Tests unitaires passants (`pytest`) — ~40% de couverture
- [x] Docker fonctionnel (`docker-compose up --build`)

### Long terme
- [x] Registre de dette rédigé (7 dettes documentées)
- [x] Risques top 5 identifiés avec parade

---

*Smart Health Habit Engine — Mariya ABAAKIL — Master 2025/2026*
