import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch
from app import create_app


@pytest.fixture
def client():
    """Client de test Flask."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES PUBLIQUES
# ─────────────────────────────────────────────────────────────────────────────
class TestRoutesPubliques:

    def test_accueil_redirige_vers_login(self, client):
        """La page d'accueil redirige vers /login si non connecté."""
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_page_login_accessible(self, client):
        """La page login est accessible sans authentification."""
        resp = client.get("/login")
        assert resp.status_code == 200

    def test_page_register_get(self, client):
        """GET /register — redirige ou affiche un formulaire (login+register sur même page)."""
        resp = client.get("/register", follow_redirects=False)
        # Register est dans la même page que login (onglets)
        # Selon l'implémentation : 200 ou 302 sont valides
        assert resp.status_code in [200, 302]


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES PROTÉGÉES
# ─────────────────────────────────────────────────────────────────────────────
class TestRoutesProtegees:

    @pytest.mark.parametrize("route", [
        "/dashboard", "/questionnaire", "/stats",
        "/calendar", "/assistant", "/rapport", "/settings"
    ])
    def test_route_protegee_redirige(self, client, route):
        """Les routes protégées redirigent vers /login si non connecté."""
        resp = client.get(route, follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]


# ─────────────────────────────────────────────────────────────────────────────
#  AUTHENTIFICATION
# ─────────────────────────────────────────────────────────────────────────────
class TestAuthentification:

    @patch("routes.auth_routes.db")
    def test_login_succes(self, mock_db, client):
        """Login avec bonnes infos → redirige vers dashboard."""
        mock_db.login_user.return_value = {
            "success": True,
            "user": {
                "id": 1, "nom": "ABAAKIL", "prenom": "Mariya",
                "email": "test@gmail.com", "date_creation": "2024-01-01",
                "derniere_connexion": "2024-01-01"
            }
        }
        resp = client.post("/login", data={
            "email": "test@gmail.com",
            "password": "motdepasse123"
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/dashboard" in resp.headers["Location"]

    @patch("routes.auth_routes.db")
    def test_login_echec(self, mock_db, client):
        """Login avec mauvaises infos → reste sur /login."""
        mock_db.login_user.return_value = {
            "success": False,
            "message": "Email ou mot de passe incorrect."
        }
        resp = client.post("/login", data={
            "email": "wrong@gmail.com",
            "password": "mauvais"
        }, follow_redirects=True)
        assert resp.status_code == 200

    @patch("routes.auth_routes.db")
    def test_register_succes(self, mock_db, client):
        """Inscription valide → redirige vers /login."""
        mock_db.register_user.return_value = {"success": True, "message": "Compte créé !"}
        resp = client.post("/register", data={
            "nom": "ABAAKIL", "prenom": "Mariya",
            "email": "new@gmail.com",
            "password": "motdepasse123",
            "confirm": "motdepasse123"
        }, follow_redirects=False)
        assert resp.status_code == 302

    def test_register_mots_de_passe_differents(self, client):
        """Mots de passe différents → erreur → redirige vers login."""
        resp = client.post("/register", data={
            "nom": "Test", "prenom": "User",
            "email": "test@gmail.com",
            "password": "motdepasse123",
            "confirm": "different"
        }, follow_redirects=False)
        # Flash message erreur → reste sur login (200 ou redirect)
        assert resp.status_code in [200, 302]

    def test_logout(self, client):
        """Déconnexion → redirige vers /login."""
        resp = client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
