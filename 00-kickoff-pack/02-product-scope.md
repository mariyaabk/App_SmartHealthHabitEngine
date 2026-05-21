## 02 — Périmètre produit (MoSCoW)

### ✅ MUST — MVP (obligatoire)

> Sans ces fonctionnalités, l'application n'a aucune valeur.

- **US-01** : En tant qu'utilisateur, je veux créer un compte (nom, prénom, email, mot de passe) afin d'accéder à mon espace personnel sécurisé.
- **US-02** : En tant qu'utilisateur connecté, je veux remplir un questionnaire quotidien (1 question à la fois) afin de suivre mes habitudes de santé.
- **US-03** : En tant qu'utilisateur connecté, je veux voir mes scores calculés automatiquement par dimension afin de comprendre mon état de bien-être.
- **US-04** : En tant qu'utilisateur connecté, je veux consulter un dashboard avec graphiques afin de visualiser mon évolution dans le temps.
- **US-05** : En tant qu'utilisateur connecté, je veux que mes données soient sauvegardées en base MySQL afin de les retrouver à chaque connexion.

### 🟡 SHOULD — V1.1

- **US-06** : En tant qu'utilisateur connecté, je veux consulter un calendrier santé coloré par score afin de voir mes jours performants d'un coup d'œil.
- **US-07** : En tant qu'utilisateur connecté, je veux télécharger un rapport PDF de mon historique afin de garder une trace de ma progression.
- **US-08** : En tant qu'utilisateur connecté, je veux recevoir une notification navigateur de rappel quotidien afin de ne pas oublier mon questionnaire.

### 🔵 COULD — Bonus si temps

- **US-09** : En tant qu'utilisateur connecté, je veux poser des questions à un assistant IA afin d'obtenir des conseils personnalisés sur ma santé.
- **US-10** : En tant qu'utilisateur connecté, je veux choisir la langue de l'interface (FR/EN) afin d'utiliser l'app dans ma langue préférée.
- **US-11** : En tant qu'utilisateur connecté, je veux envoyer mon rapport PDF par email afin de le partager facilement.

### ❌ WON'T — Hors scope assumé

- Application mobile native — délai et complexité incompatibles avec le MVP
- Comparaison des scores entre utilisateurs — pas de valeur sans masse critique

### Liste OUT — À défendre face aux ajouts

| Feature exclue | Raison |
|---|---|
| App mobile native | Trop complexe pour le MVP solo — V2 possible |
| Paiement / abonnement | Hors scope académique |
| Suivi médical avancé (glycémie, tension) | Nécessite agrément médical |
| Intégration objets connectés | Dépendances matérielles trop complexes |
| Multi-tenant / organisations | Un seul rôle utilisateur dans le MVP |