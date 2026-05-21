## 03 — Modèle métier

### 1. Rôles et permissions (RBAC)

> Un seul rôle dans le MVP : l'utilisateur authentifié. Chaque utilisateur n'accède qu'à ses propres données.

| Action | Utilisateur authentifié | Visiteur non connecté |
|---|---|---|
| Voir son dashboard | ✅ | ❌ → redirect /login |
| Remplir le questionnaire | ✅ (1 fois/jour) | ❌ |
| Voir ses statistiques | ✅ | ❌ |
| Voir les données des autres users | ❌ (isolation) | ❌ |
| Télécharger son PDF | ✅ | ❌ |
| Modifier son profil | ✅ | ❌ |
| Supprimer son compte | ✅ | ❌ |

### 2. Règles métier (numérotées)

- **RM-01** : Un email est unique dans le système — inscription refusée si déjà utilisé.
- **RM-02** : Un utilisateur ne peut remplir qu'un seul questionnaire par jour (identifié par `date_score + utilisateur_id`).
- **RM-03** : Le score global est calculé avec pondération : Sommeil 28% · Stress 22% · Activité 18% · Nutrition 17% · Concentration 15%.
- **RM-04** : Un utilisateur ne peut voir et modifier que ses propres données (vérification `utilisateur_id` à chaque requête SQL).
- **RM-05** : Le mot de passe est haché en SHA-256 avec salt — jamais stocké en clair.
- **RM-06** : Un compte supprimé entraîne la suppression en cascade de toutes ses données (habitudes, scores, conversations IA).

### 3. Machine à états — Questionnaire quotidien

```
Non commencé ──(clic questionnaire)──▶ En cours ──(dernière réponse)──▶ Complété
                                                                              │
                                                                    (état final du jour)
```

| État | Description | Transitions autorisées |
|---|---|---|
| Non commencé | Aucune entrée pour aujourd'hui | → En cours |
| En cours | L'utilisateur répond aux questions | → Complété |
| Complété | Scores calculés et sauvegardés | Aucune (état final) |

### 4. Cas d'erreur identifiés

- Tentative de remplir le questionnaire une 2e fois → redirection vers page "Déjà complété"
- Email incorrect au login → message d'erreur explicite, pas de redirection
- Connexion BDD perdue → erreur 500 avec message utilisateur propre
- Rapport PDF demandé sans données → PDF vide avec message explicatif

---