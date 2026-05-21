## ADR-002 : Choix du framework backend

**Date :** 2026-05-20
**Statut :** Accepté
**Décideurs :** Équipe projet

### Contexte
Le projet est une application web en Python avec un backend simple offrant authentification, saisie d'habitudes, dashboard et génération de PDF. L'objectif est de livrer un MVP rapidement avec une architecture maintenable.

### Options envisagées
1. Flask
2. Django
3. FastAPI

### Décision
Utiliser Flask comme framework backend principal.

### Justification
- Le code existant est déjà construit avec Flask et blueprints, ce qui évite une réécriture massive.
- Flask est léger, adapté à un monolithe MVP et permet une structure simple pour les routes, la session et les templates server-side.
- Le besoin n'impose pas une API REST à haute performance ou un schéma fortement typé généré comme avec FastAPI.
- Django est plus lourd et impose une opinion forte sur le modèle et l'ORM, ce qui rallonge le délai pour un MVP.

### Conséquences
- ✅ Livraison plus rapide avec le code existant et la structure actuelle de blueprints.
- ✅ Facilité d'évolution vers une séparation `routes -> services -> BDD` sans changer de framework.
- ⚠️ Flask ne fournit pas par défaut de gestion d'authentification avancée ou de validation de schéma, il faudra encadrer ces points manuellement.
- ⚠️ L'architecture monolithique peut nécessiter une refactorisation plus importante si le projet devient très volumineux, mais reste adaptée au MVP.
