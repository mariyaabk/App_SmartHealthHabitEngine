## 01 — Brief technique

### Problème

Les individus souhaitant améliorer leur santé quotidienne n'ont pas d'outil simple et centralisé pour suivre leurs habitudes (sommeil, stress, alimentation, sport) et recevoir des recommandations personnalisées adaptées à leur profil.

### Cible

- **Utilisateur principal** : toute personne adulte souhaitant prendre soin de sa santé au quotidien, sans consultation médicale.
- **Pain actuel** : les outils existants sont soit trop médicaux, soit trop généralistes. L'utilisateur n'a pas de vue globale sur ses habitudes ni de score pour suivre ses progrès.

### Solution proposée

Une application web permettant de remplir un questionnaire quotidien de 10 questions, de calculer automatiquement des scores de bien-être pondérés par dimension (sommeil, stress, activité, nutrition, concentration), et de visualiser son évolution dans le temps via un dashboard interactif avec graphiques, calendrier santé et assistant IA.

### Contexte projet

| Axe | Détail |
|---|---|
| Type | Projet académique (Master) |
| Équipe | 1 développeuse — Mariya ABAAKIL |
| Délai cible | MVP livré en 6 semaines |
| Stack | Python · Flask · MySQL · Tailwind · Chart.js · Docker |

### Contraintes non négociables

- Données personnelles : RGPD — email, nom, prénom, habitudes de santé
- Authentification sécurisée : hachage SHA-256 + salt, sessions Flask
- Reproductibilité : Docker + docker-compose pour tout environnement
- CI/CD : pipeline GitHub Actions automatique à chaque push

### Critère de succès

Dans 6 mois : un utilisateur peut s'inscrire, remplir son questionnaire quotidien, visualiser son évolution sur 30 jours et télécharger un rapport PDF — le tout sans aucune configuration technique de sa part.