"""
Script de réinitialisation de la base de données.
Lance ce script UNE SEULE FOIS si tu as des erreurs de colonnes manquantes.

Usage :  python reset_db.py
"""
from database.db_manager import DatabaseManager

print("⚠️  Ce script va SUPPRIMER et RECRÉER toutes les tables.")
print("    Toutes les données existantes seront perdues.")
confirm = input("Continuer ? (oui/non) : ").strip().lower()

if confirm == "oui":
    db = DatabaseManager()
    db.initialize_database()
    db.reset_database()
    print("✅ Base de données réinitialisée avec succès !")
    print("   Tu peux maintenant relancer : python app.py")
else:
    print("Annulé.")
