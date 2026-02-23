from pydantic import BaseModel

# Schéma utilisé pour la requête de connexion
class LoginRequest(BaseModel):
    # Nom d’utilisateur
    username: str
    # Mot de passe en clair (sera vérifié puis haché côté serveur)
    password: str
