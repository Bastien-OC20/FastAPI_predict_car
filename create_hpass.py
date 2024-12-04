from passlib.context import CryptContext

# Configuration de passlib pour utiliser bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hache un mot de passe en utilisant bcrypt.

    Args:
        password (str): Le mot de passe en clair à hacher.

    Returns:
        str: Le mot de passe haché.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond à un mot de passe haché.

    Args:
        plain_password (str): Le mot de passe en clair.
        hashed_password (str): Le mot de passe haché.

    Returns:
        bool: True si les mots de passe correspondent, False sinon.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Exemple d'utilisation
if __name__ == "__main__":
    password = "Sebasti1en13"
    hashed_password = get_password_hash(password)
    print(f"Mot de passe haché : {hashed_password}")

    # Vérification du mot de passe
    is_valid = verify_password(password, hashed_password)
    print(f"Le mot de passe est valide : {is_valid}")