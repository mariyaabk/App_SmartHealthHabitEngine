"""Envoi email avec pièce jointe PDF."""
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from config.settings import EMAIL_CONFIG


class EmailSender:

    def send_with_credentials(self, dest_email, sender_email, sender_password,
                               pdf_path, user, stats):
        """
        Envoie le PDF par email en utilisant les credentials fournis directement.
        Aucune configuration dans settings.py requise.
        """
        if not sender_email or not sender_password:
            raise ValueError("Email expéditeur et App Password requis.")
        if not sender_email.endswith("@gmail.com"):
            raise ValueError("L'email expéditeur doit être un compte Gmail (@gmail.com).")

        msg = self._build_message(
            sender=sender_email,
            dest=dest_email,
            pdf_path=pdf_path,
            user=user,
            stats=stats,
        )

        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
                s.ehlo()
                s.starttls()
                s.login(sender_email, sender_password)
                s.sendmail(sender_email, dest_email, msg.as_string())
        except smtplib.SMTPAuthenticationError:
            raise ValueError(
                "Authentification Gmail échouée.\n"
                "Vérifie que tu utilises bien un App Password (16 caractères),\n"
                "pas ton mot de passe Gmail habituel.\n\n"
                "Créer un App Password : myaccount.google.com → Sécurité → "
                "Validation en 2 étapes → Mots de passe des applications"
            )
        except smtplib.SMTPException as e:
            raise ValueError(f"Erreur SMTP : {e}")

    def send_plain_email(self, dest_email: str, subject: str, html_body: str):
        """Envoie un email HTML simple en utilisant SMTP."""
        sender_email = EMAIL_CONFIG.get("sender_email", "")
        sender_password = EMAIL_CONFIG.get("sender_password", "")
        smtp_server = EMAIL_CONFIG.get("smtp_server", "smtp.gmail.com")
        smtp_port = EMAIL_CONFIG.get("smtp_port", 587)

        if not sender_email or not sender_password:
            raise ValueError(
                "Email expéditeur non configuré. Configure SENDER_EMAIL et SENDER_PASSWORD."
            )

        msg = MIMEText(html_body, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = dest_email

        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as s:
                s.ehlo()
                s.starttls()
                s.login(sender_email, sender_password)
                s.sendmail(sender_email, dest_email, msg.as_string())
        except smtplib.SMTPException as e:
            raise ValueError(f"Erreur SMTP : {e}")

    def _build_message(self, sender, dest, pdf_path, user, stats):
        msg = MIMEMultipart()
        msg["Subject"] = f"🧠 Votre rapport SHHE — {datetime.date.today().strftime('%d/%m/%Y')}"
        msg["From"] = sender
        msg["To"] = dest

        prenom = user.get("prenom", "")
        nom    = user.get("nom", "")
        score  = f"{stats.get('moyenne_globale') or 0:.1f}" if stats.get("moyenne_globale") else "N/A"
        jours  = int(stats.get("total_jours") or 0)

        html = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;color:#1f2937">
          <div style="background:linear-gradient(135deg,#0288d1,#7b1fa2);padding:30px;border-radius:12px 12px 0 0">
            <h1 style="color:white;margin:0">🧠 Smart Health Habit Engine</h1>
            <p style="color:#e0e0e0;margin:6px 0 0">Rapport de bien-être personnel</p>
          </div>
          <div style="background:#f8fafc;padding:25px;border-radius:0 0 12px 12px">
            <p>Bonjour <strong>{prenom} {nom}</strong> ! 👋</p>
            <p>Votre rapport de bien-être est disponible en pièce jointe.</p>
            <div style="background:white;border-radius:8px;padding:20px;margin:15px 0;border:1px solid #e5e7eb">
              <p>🌟 <strong>Score moyen global :</strong> {score}/100</p>
              <p>📅 <strong>Jours de suivi :</strong> {jours} jour(s)</p>
            </div>
            <p style="color:#6b7280;font-size:12px;margin-top:20px">
              Ce rapport a été généré automatiquement par Smart Health Habit Engine.
            </p>
          </div>
        </body></html>
        """
        msg.attach(MIMEText(html, "html", "utf-8"))

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition",
                                f'attachment; filename="{os.path.basename(pdf_path)}"')
                msg.attach(part)
        return msg

    # Compatibilité ancienne API (si utilisée ailleurs)
    def send(self, dest_email, pdf_path, user, stats):
        from config.settings import EMAIL_CONFIG
        cfg = EMAIL_CONFIG
        if not cfg.get("sender_email") or "ton_email" in cfg.get("sender_email", ""):
            raise ValueError("Email non configuré. Utilisez la méthode send_with_credentials().")
        self.send_with_credentials(
            dest_email=dest_email,
            sender_email=cfg["sender_email"],
            sender_password=cfg["sender_password"],
            pdf_path=pdf_path,
            user=user,
            stats=stats,
        )
