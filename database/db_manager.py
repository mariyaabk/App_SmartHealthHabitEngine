"""
Gestionnaire de base de données MySQL.
Gère la connexion, la création/réinitialisation des tables et le CRUD.
"""

import mysql.connector
from mysql.connector import Error
from config.settings import DB_CONFIG
import hashlib


class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG

    # ─────────────────────────────────────────
    #  CONNEXION
    # ─────────────────────────────────────────
    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            raise ConnectionError(f"Erreur MySQL : {e}")

    # ─────────────────────────────────────────
    #  INITIALISATION
    # ─────────────────────────────────────────
    def initialize_database(self):
        """Crée la BDD et les tables (recrée si schéma obsolète)."""
        config_no_db = {k: v for k, v in self.config.items() if k != "database"}
        try:
            conn = mysql.connector.connect(**config_no_db)
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.config['database']}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            raise ConnectionError(f"Impossible de créer la BDD : {e}")

        self._create_tables()
        print("✅ Base de données prête.")

    def reset_database(self):
        """Supprime et recrée toutes les tables (utile en dev)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in ["conversations_ia", "rappels", "scores", "habitudes", "utilisateurs"]:
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        cursor.close()
        conn.close()
        self._create_tables()
        print("🔄 Tables réinitialisées.")

    def _create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        tables = [
            # ── utilisateurs ──────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id                     INT AUTO_INCREMENT PRIMARY KEY,
                nom                    VARCHAR(100)        NOT NULL,
                prenom                 VARCHAR(100)        NOT NULL,
                email                  VARCHAR(255) UNIQUE NOT NULL,
                mot_de_passe           VARCHAR(255)        NOT NULL,
                reminder_time          TIME NOT NULL DEFAULT '20:00',

                date_creation          DATETIME DEFAULT CURRENT_TIMESTAMP,
                derniere_connexion     DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            # ── habitudes ─────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS habitudes (
                id                  INT AUTO_INCREMENT PRIMARY KEY,
                utilisateur_id      INT     NOT NULL,
                date_enregistrement DATE    NOT NULL,
                heure_sommeil       FLOAT   NOT NULL,
                qualite_sommeil     INT     NOT NULL,
                niveau_stress       INT     NOT NULL,
                concentration       INT     NOT NULL,
                temps_ecran         FLOAT   NOT NULL,
                sport               INT     NOT NULL,
                cafeine             INT     NOT NULL,
                humeur              INT     NOT NULL,
                hydratation         FLOAT   NOT NULL,
                repas_equilibre     INT     NOT NULL,
                UNIQUE KEY uniq_user_date (utilisateur_id, date_enregistrement),
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            # ── scores ────────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS scores (
                id                  INT AUTO_INCREMENT PRIMARY KEY,
                habitude_id         INT     NOT NULL UNIQUE,
                utilisateur_id      INT     NOT NULL,
                date_score          DATE    NOT NULL,
                score_sommeil       FLOAT   NOT NULL,
                score_stress        FLOAT   NOT NULL,
                score_concentration FLOAT   NOT NULL,
                score_activite      FLOAT   NOT NULL,
                score_nutrition     FLOAT   NOT NULL,
                score_global        FLOAT   NOT NULL,
                niveau              VARCHAR(20) NOT NULL,
                FOREIGN KEY (habitude_id)    REFERENCES habitudes(id)    ON DELETE CASCADE,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            # ── rappels ───────────────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS rappels (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                utilisateur_id INT NOT NULL,
                message        TEXT NOT NULL,
                heure_envoi    TIME NOT NULL,
                actif          TINYINT(1) DEFAULT 1,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,

            # ── conversations_ia ──────────────────────────────────────────
            """
            CREATE TABLE IF NOT EXISTS conversations_ia (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                utilisateur_id INT  NOT NULL,
                question       TEXT NOT NULL,
                reponse        TEXT NOT NULL,
                date_heure     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
        ]

        for sql in tables:
            cursor.execute(sql)

        # Vérifier que les colonnes critiques existent (migration douce)
        self._migrate_if_needed(cursor)

        conn.commit()
        cursor.close()
        conn.close()

    def _migrate_if_needed(self, cursor):
        """Ajoute les colonnes manquantes si la table existait déjà avec un ancien schéma."""
        try:
            cursor.execute("SHOW COLUMNS FROM habitudes LIKE 'utilisateur_id'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE habitudes ADD COLUMN utilisateur_id INT NOT NULL AFTER id")
                print("🔧 Migration : colonne utilisateur_id ajoutée à habitudes.")
        except Exception:
            pass

        try:
            cursor.execute("SHOW COLUMNS FROM habitudes LIKE 'hydratation'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE habitudes ADD COLUMN hydratation FLOAT NOT NULL DEFAULT 1.5")
                cursor.execute("ALTER TABLE habitudes ADD COLUMN repas_equilibre INT NOT NULL DEFAULT 1")
                print("🔧 Migration : colonnes hydratation/repas_equilibre ajoutées.")
        except Exception:
            pass

        # Colonnes pour les notifications email
        try:
            cursor.execute("SHOW COLUMNS FROM utilisateurs LIKE 'email_notif'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE utilisateurs ADD COLUMN email_notif VARCHAR(255) DEFAULT NULL")
                print("🔧 Migration : colonne email_notif ajoutée à utilisateurs.")
        except Exception:
            pass

        try:
            cursor.execute("SHOW COLUMNS FROM utilisateurs LIKE 'reminder_time'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE utilisateurs ADD COLUMN reminder_time TIME DEFAULT NULL")
                print("🔧 Migration : colonne reminder_time ajoutée à utilisateurs.")
        except Exception:
            pass

        try:
            cursor.execute("SHOW COLUMNS FROM utilisateurs LIKE 'last_reminder_date'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE utilisateurs ADD COLUMN last_reminder_date DATE DEFAULT NULL")
                print("🔧 Migration : colonne last_reminder_date ajoutée à utilisateurs.")
        except Exception:
            pass


    # ─────────────────────────────────────────
    #  AUTHENTIFICATION
    # ─────────────────────────────────────────
    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(("SHHE_SALT_2024" + password).encode()).hexdigest()

    def register_user(self, nom, prenom, email, password) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM utilisateurs WHERE email=%s", (email,))
            if cursor.fetchone():
                return {"success": False, "message": "Cet email est déjà utilisé."}
            cursor.execute(
                "INSERT INTO utilisateurs (nom,prenom,email,mot_de_passe) VALUES (%s,%s,%s,%s)",
                (nom, prenom, email, self._hash(password))
            )
            conn.commit()
            return {"success": True, "message": "Compte créé !"}
        except Error as e:
            return {"success": False, "message": str(e)}
        finally:
            cursor.close(); conn.close()

    def login_user(self, email, password) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM utilisateurs WHERE email=%s AND mot_de_passe=%s",
                (email, self._hash(password))
            )
            user = cursor.fetchone()
            if user:
                cursor.execute("UPDATE utilisateurs SET derniere_connexion=NOW() WHERE id=%s", (user["id"],))
                conn.commit()
                # Convertir les dates/temps en string pour la session Flask
                for key in ["date_creation", "derniere_connexion", "reminder_time"]:
                    if user.get(key) is not None:
                        user[key] = str(user[key])
                return {"success": True, "user": user}
            return {"success": False, "message": "Email ou mot de passe incorrect."}
        finally:
            cursor.close(); conn.close()

    # ─────────────────────────────────────────
    #  HABITUDES & SCORES
    # ─────────────────────────────────────────
    def save_habitude(self, utilisateur_id: int, data: dict) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO habitudes
                    (utilisateur_id, date_enregistrement, heure_sommeil, qualite_sommeil,
                     niveau_stress, concentration, temps_ecran, sport, cafeine,
                     humeur, hydratation, repas_equilibre)
                VALUES (%s, CURDATE(), %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    heure_sommeil=VALUES(heure_sommeil), qualite_sommeil=VALUES(qualite_sommeil),
                    niveau_stress=VALUES(niveau_stress), concentration=VALUES(concentration),
                    temps_ecran=VALUES(temps_ecran),     sport=VALUES(sport),
                    cafeine=VALUES(cafeine),             humeur=VALUES(humeur),
                    hydratation=VALUES(hydratation),     repas_equilibre=VALUES(repas_equilibre)
            """
            cursor.execute(sql, (
                utilisateur_id,
                data["heure_sommeil"], data["qualite_sommeil"],
                data["niveau_stress"], data["concentration"],
                data["temps_ecran"],   data["sport"],
                data["cafeine"],       data["humeur"],
                data["hydratation"],   data["repas_equilibre"]
            ))
            conn.commit()
            # Récupérer l'id (INSERT ou UPDATE)
            if cursor.lastrowid:
                return cursor.lastrowid
            cursor.execute(
                "SELECT id FROM habitudes WHERE utilisateur_id=%s AND date_enregistrement=CURDATE()",
                (utilisateur_id,)
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close(); conn.close()

    def save_score(self, utilisateur_id: int, habitude_id: int, scores: dict):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO scores
                    (habitude_id, utilisateur_id, date_score,
                     score_sommeil, score_stress, score_concentration,
                     score_activite, score_nutrition, score_global, niveau)
                VALUES (%s,%s,CURDATE(),%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    score_sommeil=VALUES(score_sommeil), score_stress=VALUES(score_stress),
                    score_concentration=VALUES(score_concentration),
                    score_activite=VALUES(score_activite), score_nutrition=VALUES(score_nutrition),
                    score_global=VALUES(score_global),   niveau=VALUES(niveau)
            """
            cursor.execute(sql, (
                habitude_id, utilisateur_id,
                scores["score_sommeil"],       scores["score_stress"],
                scores["score_concentration"], scores["score_activite"],
                scores["score_nutrition"],     scores["score_global"],
                scores["niveau"]
            ))
            conn.commit()
        finally:
            cursor.close(); conn.close()

    def get_historique(self, utilisateur_id: int, limit: int = 30) -> list:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT s.*, h.heure_sommeil, h.niveau_stress, h.concentration,
                       h.sport, h.humeur, h.cafeine, h.hydratation, h.temps_ecran,
                       h.repas_equilibre, h.qualite_sommeil
                FROM scores s
                JOIN habitudes h ON s.habitude_id = h.id
                WHERE s.utilisateur_id = %s
                ORDER BY s.date_score DESC
                LIMIT %s
            """, (utilisateur_id, limit))
            rows = cursor.fetchall()
            # Convertir les dates en string
            for row in rows:
                if row.get("date_score"):
                    row["date_score"] = str(row["date_score"])
            return rows
        finally:
            cursor.close(); conn.close()

    def a_deja_repondu_aujourd_hui(self, utilisateur_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM habitudes WHERE utilisateur_id=%s AND date_enregistrement=CURDATE()",
                (utilisateur_id,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close(); conn.close()

    def get_statistiques(self, utilisateur_id: int) -> dict:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    COUNT(*)                     AS total_jours,
                    ROUND(AVG(score_global),1)   AS moyenne_globale,
                    ROUND(MAX(score_global),1)   AS meilleur_score,
                    ROUND(MIN(score_global),1)   AS pire_score,
                    ROUND(AVG(score_sommeil),1)  AS moy_sommeil,
                    ROUND(AVG(score_stress),1)   AS moy_stress,
                    ROUND(AVG(score_concentration),1) AS moy_concentration,
                    ROUND(AVG(score_activite),1) AS moy_activite,
                    ROUND(AVG(score_nutrition),1) AS moy_nutrition
                FROM scores WHERE utilisateur_id=%s
            """, (utilisateur_id,))
            return cursor.fetchone() or {}
        finally:
            cursor.close(); conn.close()

    def save_conversation_ia(self, utilisateur_id, question, reponse):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO conversations_ia (utilisateur_id,question,reponse) VALUES (%s,%s,%s)",
                (utilisateur_id, question, reponse)
            )
            conn.commit()
        finally:
            cursor.close(); conn.close()

    def get_conversations_ia(self, utilisateur_id, limit=20) -> list:
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT question, reponse, date_heure FROM conversations_ia "
                "WHERE utilisateur_id=%s ORDER BY date_heure DESC LIMIT %s",
                (utilisateur_id, limit)
            )
            rows = cursor.fetchall()
            for row in rows:
                if row.get("date_heure"):
                    row["date_heure"] = str(row["date_heure"])
            return rows
        finally:
            cursor.close(); conn.close()

    def login_or_create_oauth(self, email: str, prenom: str, nom: str, provider: str) -> dict:
        """
        Connecte ou crée un utilisateur via OAuth (Google/Facebook).
        Si l'email existe déjà → connexion directe.
        Sinon → création automatique sans mot de passe.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Vérifier si l'utilisateur existe
            cursor.execute("SELECT * FROM utilisateurs WHERE email=%s", (email,))
            user = cursor.fetchone()

            if not user:
                # Créer le compte automatiquement
                cursor.execute(
                    "INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe) VALUES (%s,%s,%s,%s)",
                    (nom or "—", prenom or "—", email, f"oauth_{provider}_{email}")
                )
                conn.commit()
                cursor.execute("SELECT * FROM utilisateurs WHERE email=%s", (email,))
                user = cursor.fetchone()

            # Mettre à jour la dernière connexion
            cursor.execute("UPDATE utilisateurs SET derniere_connexion=NOW() WHERE id=%s", (user["id"],))
            conn.commit()

            # Sérialiser les dates et heures pour la session Flask
            for key in ["date_creation", "derniere_connexion", "reminder_time"]:
                if user.get(key) is not None:
                    user[key] = str(user[key])

            return {"success": True, "user": user}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def update_profile(self, user_id: int, nom: str, prenom: str, email: str,
                       reminder_time: str = None) -> dict:
        """Modifier le profil d'un utilisateur."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Vérifier que l'email n'est pas déjà utilisé par quelqu'un d'autre
            cursor.execute(
                "SELECT id FROM utilisateurs WHERE email=%s AND id != %s",
                (email, user_id)
            )
            if cursor.fetchone():
                return {"success": False, "message": "Cet email est déjà utilisé par un autre compte."}

            sql = "UPDATE utilisateurs SET nom=%s, prenom=%s, email=%s"
            params = [nom, prenom, email]

            if reminder_time is not None:
                sql += ", reminder_time=%s"
                params.append(reminder_time)

            sql += " WHERE id=%s"
            params.append(user_id)

            cursor.execute(sql, tuple(params))
            conn.commit()
            return {"success": True, "message": "Profil mis à jour avec succès !"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            cursor.close()
            conn.close()


    def delete_account(self, user_id: int) -> dict:
        """Supprimer définitivement un compte et toutes ses données."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Les FK ON DELETE CASCADE suppriment automatiquement les données liées
            cursor.execute("DELETE FROM utilisateurs WHERE id=%s", (user_id,))
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    def get_current_mysql_time(self) -> str:
        """Retourne l'heure courante au format HH:MM selon MySQL (timezone du serveur MySQL)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT TIME_FORMAT(NOW(), '%H:%i') as heure")
            row = cursor.fetchone()
            return row[0] if row else "00:00"
        finally:
            cursor.close()
            conn.close()

    def get_users_for_reminder(self, heure: str) -> list:
        """
        Retourne tous les users qui ont configuré un rappel email
        pour l'heure donnée (format HH:MM) et n'ont pas encore
        reçu leur rappel aujourd'hui.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, prenom, nom, email, email_notif, reminder_time
                FROM utilisateurs
                WHERE TIME_FORMAT(reminder_time, '%H:%i') = %s
                  AND email_notif IS NOT NULL
                  AND email_notif != ''
                  AND (last_reminder_date IS NULL OR last_reminder_date < CURDATE())
            """, (heure,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def mark_reminder_sent(self, user_id: int):
        """Marque le rappel comme envoyé aujourd'hui pour cet user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE utilisateurs SET last_reminder_date = CURDATE() WHERE id = %s",
                (user_id,)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_notif_settings(self, user_id: int, email_notif: str, reminder_time: str) -> dict:
        """Sauvegarde l'email de notif et l'heure de rappel d'un user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE utilisateurs SET email_notif=%s, reminder_time=%s WHERE id=%s",
                (email_notif, reminder_time, user_id)
            )
            conn.commit()
            return {"success": True, "message": "Paramètres de notification sauvegardés !"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            cursor.close()
            conn.close()