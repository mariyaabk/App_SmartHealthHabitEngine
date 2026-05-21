## 04 — Base de données

### Choix moteur

**MySQL 8.0** — données fortement relationnelles, équipe maîtrise SQL, visualisable via Workbench. Voir ADR-001.

### ERD — Relations entre tables

┌──────────────────────┐                    ┌──────────────────────┐
│    utilisateurs      │ 1              N   │      habitudes       │
│──────────────────────│────────────────────│──────────────────────│
│ id            PK     │                    │ id              PK   │
│ nom                  │                    │ utilisateur_id  FK   │
│ prenom               │                    │ date_enregistrement  │
│ email         UNIQUE │                    │ heure_sommeil        │
│ mot_de_passe         │                    │ qualite_sommeil      │
│ date_creation        │                    │ niveau_stress        │
│ derniere_connexion   │                    │ concentration        │
│ email_notif          │                    │ humeur               │
│ reminder_time        │                    │ sport                │
│ last_reminder_date   │                    │ temps_ecran          │
└──────────────────────┘                    │ cafeine              │
           │                                │ hydratation          │
           │                                │ repas_equilibre      │
           │                                └──────────────────────┘
           │                                          │
           │                                          │ 1
           │                                          │
           │                                          │ 1
           │                                ┌──────────────────────┐
           │                                │        scores        │
           │                                │──────────────────────│
           │                                │ id              PK   │
           │                                │ habitude_id     FK   │
           │                                │ utilisateur_id  FK   │
           │                                │ date_score           │
           │ 1                              │ score_sommeil        │
           │                                │ score_stress         │
           ├────────────────────────────────│ score_concentration  │
           │                                │ score_activite       │
           │ 1               N              │ score_nutrition      │
           │                                │ score_global         │
           │                                │ niveau               │
           │                                └──────────────────────┘
           │
           │ 1               N              ┌──────────────────────┐
           │                                │   conversations_ia   │
           ├────────────────────────────────│──────────────────────│
           │                                │ id              PK   │
           │                                │ utilisateur_id  FK   │
           │                                │ question             │
           │                                │ reponse              │
           │                                │ date_heure           │
           │                                └──────────────────────┘
           │
           │ 1               N              ┌──────────────────────┐
           │                                │       rappels        │
           └────────────────────────────────│──────────────────────│
                                            │ id              PK   │
                                            │ utilisateur_id  FK   │
                                            │ message              │
                                            │ heure_envoi          │
                                            │ actif                │
                                            └──────────────────────┘

### Dictionnaire de données

**Table : `utilisateurs`**

| Colonne | Type | Contraintes | Description |
|---|---|---|---|
| id | INT AUTO_INCREMENT | PK, NOT NULL | Identifiant unique |
| nom | VARCHAR(100) | NOT NULL | Nom de famille |
| prenom | VARCHAR(100) | NOT NULL | Prénom |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email d'authentification |
| mot_de_passe | VARCHAR(255) | NOT NULL | SHA-256 + salt |
| date_creation | DATETIME | DEFAULT NOW() | Création du compte |
| derniere_connexion | DATETIME | NULL | Dernière connexion |
| email_notif | VARCHAR(255) | NULL | Email rappel quotidien |
| reminder_time | TIME | NULL | Heure de rappel |
| last_reminder_date | DATE | NULL | Dernier rappel envoyé |

**Table : `habitudes`**

| Colonne | Type | Description |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identifiant |
| utilisateur_id | INT FK → utilisateurs | Propriétaire |
| date_enregistrement | DATE NOT NULL, UNIQUE(utilisateur_id) | Date du questionnaire |
| heure_sommeil | FLOAT | Heures de sommeil |
| qualite_sommeil | INT (1-4) | Qualité du sommeil |
| niveau_stress | INT (1-5) | Niveau de stress |
| concentration | INT (1-5) | Concentration |
| humeur | INT (1-5) | Humeur générale |
| sport | INT | Minutes d'activité physique |
| temps_ecran | FLOAT | Heures d'écran |
| cafeine | INT | Tasses de café/thé |
| hydratation | FLOAT | Litres d'eau |
| repas_equilibre | INT (0/1) | Repas équilibré |

**Table : `scores`**

| Colonne | Type | Description |
|---|---|---|
| id | INT AUTO_INCREMENT PK | Identifiant |
| habitude_id | INT FK UNIQUE | Lié à une habitude |
| utilisateur_id | INT FK | Propriétaire |
| date_score | DATE | Date du score |
| score_sommeil | FLOAT | Score dimension sommeil /100 |
| score_stress | FLOAT | Score dimension stress /100 |
| score_concentration | FLOAT | Score dimension concentration /100 |
| score_activite | FLOAT | Score dimension activité /100 |
| score_nutrition | FLOAT | Score dimension nutrition /100 |
| score_global | FLOAT | Score pondéré global /100 |
| niveau | VARCHAR(20) | Excellent/Bon/Moyen/Faible/Critique |

### Anti-patterns évités

- ✅ Pas de table fourre-tout : 5 tables avec rôles distincts
- ✅ Pas de valeurs multiples dans une cellule
- ✅ IDs auto-incrémentés non exposés dans les URLs
- ✅ Contrainte UNIQUE sur `(utilisateur_id, date_enregistrement)` dans habitudes

---
