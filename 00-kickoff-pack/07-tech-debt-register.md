## 07 — Registre de dette technique

### Dettes acceptées au démarrage

| # | Dette | Pourquoi maintenant | Coût futur | Plan |
|---|---|---|---|---|
| 1 | SHA-256 au lieu de bcrypt | MVP rapide, compétence disponible | 2 jours migration | V1.1 |
| 2 | Pas de rate limiting /login | MVP sans risque prod | 1 jour | V1.1 |
| 3 | Pas d'audit log | Non critique au MVP | 3 jours | V2 |
| 4 | Secrets dans settings.py | Pas de vault configuré | 1 jour (variables env) | V1.1 |
| 5 | Pas de soft delete | MVP simple | Migration + 2 jours | V2 |
| 6 | Pas de migrations versionnées | Tables créées auto au boot | Alembic — 2 jours | V2 |
| 7 | HTTPS non configuré | Localhost dev uniquement | Certificat + nginx — 1 jour | Prod |

### Risques techniques identifiés (Top 5)

| # | Risque | Catégorie | Probabilité | Impact | Parade |
|---|---|---|---|---|---|
| 1 | BDD lente à 10K users | Scalabilité | Moyenne | Élevé | Index sur FK + colonnes filtrées |
| 2 | Injection SQL si requête non préparée | Sécurité | Faible | Critique | Requêtes préparées systématiques |
| 3 | Décalage timezone Docker/MySQL | Infra | Réalisé | Moyen | `TZ=Europe/Paris` dans docker-compose |
| 4 | Perte données si delete sans cascade | BDD | Faible | Élevé | FK avec ON DELETE CASCADE |
| 5 | Thread rappel email silencieux | Observabilité | Moyenne | Moyen | Logs `[ReminderService]` en console |
