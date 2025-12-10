def hash_password(mot_de_passe: str) -> str:
    """
    Hache un mot de passe avec un sel (salt) aléatoire.
    Retourne une chaîne contenant le sel et le hachage.
    """

    import hashlib
    import secrets
    import base64

    # Génère un sel cryptographiquement sûr (16 octets)
    sel = secrets.token_bytes(16)

    # Utilise PBKDF2 avec SHA256 — standard sécurisé
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',               # algorithme
        mot_de_passe.encode(),  # mot de passe en bytes
        sel,                    # sel
        100_000                 # nombre d’itérations (sécurité)
    )

    # Combine le sel + hash et encode en base64 pour stockage
    return base64.b64encode(sel + hash_bytes).decode()

def verify_password(mot_de_passe: str, hash_stocke: str) -> bool:
    """
    Vérifie si un mot de passe correspond au hachage stocké.
    """

    import hashlib
    import secrets
    import base64

    donnees = base64.b64decode(hash_stocke.encode())
    sel = donnees[:16]
    hash_attendu = donnees[16:]

    # Recalcule le hash avec le même sel
    hash_test = hashlib.pbkdf2_hmac(
        'sha256',
        mot_de_passe.encode(),
        sel,
        100_000
    )

    # Compare de manière sûre
    return secrets.compare_digest(hash_attendu, hash_test)

def get_password_entropy(mdp: str, pools_used: int | None = None) -> float:
    import math

    """
    Estime l'entropie (en bits) comme approximation: bits = longueur * log2(taille_de_l_alphabet)
    Si pools_used fournie, on utilisera sa taille comme alphabet, sinon on dérive depuis le mot de passe.
    """
    if pools_used is None:
        # approx. taille de l'alphabet utilisé par observation
        alphabet = set(mdp)
        alpha_size = len(alphabet)
    else:
        alpha_size = pools_used

    if alpha_size <= 1:
        return 0.0
    return len(mdp) * math.log2(alpha_size)

def get_password_strength(password: str, pool_size: int | None = None) -> int:
    """
    Évalue un mot de passe et renvoie son niveau de sécurité
    basé sur l'entropie calculée.
    """
    strength = 1

    # 1. Calculer l'entropie en bits
    if not pool_size:
        pool_size = get_automatic_pool_size(password)

    entropy = get_password_entropy(password, pool_size)

    # 2. Définir les niveaux de sécurité
    if entropy < 60:
        strength = 1 #f"Faible 🔴 ({entropy:.1f} bits)"
    elif entropy < 80:
        strength = 2 #f"Moyen 🟡 ({entropy:.1f} bits)"
    elif entropy < 128:
        strength = 3 #f"Fort 🟢 ({entropy:.1f} bits)"
    else:
        # 128 bits et plus
        strength = 4 #f"Excellent 🔵 ({entropy:.1f} bits)"
    
    return {"strength":strength, "entropy":entropy, "pool_size":pool_size}

def get_automatic_pool_size(password: str) -> int:
    """
    Détermine la taille du pool (alphabet) en examinant le mot de passe
    et en identifiant les catégories de caractères utilisées (minuscules,
    majuscules, chiffres, symboles).
    """
    import string
   
    pool_size = 0
    
    # Indicateurs des ensembles de caractères utilisés
    has_lower = False
    has_upper = False
    has_digit = False
    has_symbol = False
    
    # 1. Analyser chaque caractère du mot de passe
    for char in password:
        if char in string.ascii_lowercase:
            has_lower = True
        elif char in string.ascii_uppercase:
            has_upper = True
        elif char in string.digits:
            has_digit = True
        # Les caractères restants sont considérés comme des symboles
        elif char in string.punctuation or char in string.whitespace:
            has_symbol = True
        # Note: Les caractères unicode non ASCII sont ignorés ou considérés comme symboles

    # 2. Additionner les tailles des ensembles utilisés
    
    # Minuscules (a-z) : 26
    if has_lower:
        pool_size += 26
        
    # Majuscules (A-Z) : 26
    if has_upper:
        pool_size += 26
        
    # Chiffres (0-9) : 10
    if has_digit:
        pool_size += 10
        
    # Symboles courants : estimation à 32
    # string.punctuation contient 32 symboles standards (!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~)
    if has_symbol:
        # On utilise généralement 32 ou plus pour les symboles courants
        pool_size += 32 
        
    # 3. Retourner la taille totale du pool estimé
    return pool_size