## ADR-003 : Stratégie d'authentification

**Date :** 2026-05-20
**Statut :** Accepté
**Décideurs :** Équipe projet

### Contexte
L'application doit fournir un espace utilisateur sécurisé pour suivre des habitudes personnelles et générer des rapports. L'objectif MVP est de protéger les données utilisateur sans complexifier l'implémentation initiale.

### Options envisagées
1. Authentification session Flask avec email/mot de passe
2. Authentification JWT
3. Authentification OAuth (Google/Facebook)

### Décision
Utiliser l'authentification session Flask avec email et mot de passe haché.

### Justification
- Le projet est un MVP avec une interface server-side et des pages protégées par session ; Flask gère naturellement les sessions.
- JWT introduit une complexité inutile pour l'état de session utilisateur et la gestion des refresh tokens dans cette phase.
- OAuth ajouterait des dépendances externes et ne répond pas au besoin critique du MVP.
- La gestion d'email/mot de passe est la solution la plus simple et réversible pour des utilisateurs uniques.

### Conséquences
- ✅ Implémentation actuelle avec `DatabaseManager.register_user()` et `login_user()` reste valide.
- ✅ Simplicité pour les pages protégées par `session["user"]` et l'usage de blueprints Flask.
- ⚠️ Le hachage SHA-256 actuel n'est pas optimal pour la production ; il faudra migrer vers bcrypt ou Argon2 pour une meilleure sécurité.
- ⚠️ Aucune prise en charge d'OAuth n'est prévue pour le MVP, ce qui limite les options de login social.
- ⚠️ Le passage à JWT nécessitera une future refactorisation de la gestion des sessions et de l'expiration des tokens.
