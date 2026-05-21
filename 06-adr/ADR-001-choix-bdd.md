## ADR-001 : Choix de la base de données principale

**Date :** 2026-05-20
**Statut :** Accepté
**Décideurs :** Équipe projet

### Contexte
Le projet Smart Health Habit Engine est une application web monolithique de suivi d'habitudes santé. Les données sont relationnelles : utilisateurs, habitudes journalières, scores calculés, rappels et conversations IA.

### Options envisagées
1. MySQL 8.0
2. PostgreSQL 16
3. MongoDB

### Décision
Utiliser MySQL 8.0 comme moteur de base de données principale.

### Justification
- Le projet est déjà construit autour de MySQL et la configuration Docker actuelle utilise MySQL 8.0.
- Les entités sont fortement relationnelles et requièrent des contraintes `UNIQUE`, des clés étrangères et des transactions simples.
- L'équipe a déjà une implémentation fonctionnelle en MySQL, ce qui minimise le temps de livraison du MVP.
- MySQL offre une maturité, une large communauté et un coût opérationnel faible pour le MVP.

### Conséquences
- ✅ Utilisation immédiate de l'infrastructure existante dans `docker-compose.yml` et `database/db_manager.py`.
- ✅ Schéma relationnel clair avec contraintes de base et intégrité référentielle.
- ⚠️ En cas de migration future vers PostgreSQL, des adaptations SQL et des tests de compatibilité seront nécessaires.
- ⚠️ MySQL est moins souple que PostgreSQL pour certains types JSONB et fonctions analytiques avancées, mais ces besoins ne sont pas prioritaires pour le MVP.
