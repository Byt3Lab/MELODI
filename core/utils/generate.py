def gen_id_by_uuid4(prefix: str = "") -> str:
    from uuid import uuid4
    id = prefix + str(uuid4())
    return id

def gen_id_by_hash(nom: str) -> str:
    import hashlib
    import time

    """Génère un ID unique basé sur le nom et l'heure actuelle."""
    base = f"{nom}-{time.time()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16]  # 16 caractères

def random_password(
    longueur: int = 16,
    use_lower: bool = True,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    avoid_ambiguous: bool = True,
    ambiguous_chars: list[str] | None = None,
) -> str:
    import string
    import secrets
    import random

    """
    Génère un mot de passe sécurisé.

    Paramètres
    ----------
    longueur : int
        longueur souhaitée du mot de passe (doit être >= nombre de catégories activées).
    use_lower, use_upper, use_digits, use_symbols : bool
        inclure minuscules / majuscules / chiffres / symboles.
    avoid_ambiguous : bool
        si True, enlève les caractères ambigus (ex: 'O', '0', 'l', 'I').
    ambiguous_chars : Optional[str]
        chaîne de caractères considérée comme ambigüe (si fournie, on l'utilise).

    Retour
    ------
    str
        mot de passe généré.
    """

    if ambiguous_chars is None:
        ambiguous_chars = "O0oIl1|`'\""

    categories = []
    if use_lower:
        categories.append('lower')
    if use_upper:
        categories.append('upper')
    if use_digits:
        categories.append('digits')
    if use_symbols:
        categories.append('symbols')

    if not categories:
        raise ValueError("Au moins une catégorie (lower/upper/digits/symbols) doit être activée.")

    if longueur < len(categories):
        raise ValueError(f"longueur trop petite: doit être >= {len(categories)} pour garantir 1 char/category.")

    # Construire les jeux de caractères
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?/"

    # Éviter ambigus si demandé
    if avoid_ambiguous:
        for ch in ambiguous_chars:
            lower = lower.replace(ch, "")
            upper = upper.replace(ch, "")
            digits = digits.replace(ch, "")
            symbols = symbols.replace(ch, "")

    pools = {}
    if use_lower and lower:
        pools['lower'] = lower
    if use_upper and upper:
        pools['upper'] = upper
    if use_digits and digits:
        pools['digits'] = digits
    if use_symbols and symbols:
        pools['symbols'] = symbols

    # S'assurer qu'il reste des caractères dans chaque pool
    for name, pool in pools.items():
        if not pool:
            raise ValueError(f"Après suppression des caractères ambigus, le pool '{name}' est vide.")

    # Garantie : au moins un caractère de chaque catégorie choisie
    password_chars = [secrets.choice(pools[c]) for c in pools]

    # Remplir le reste des caractères à partir de l'union des pools
    all_chars = "".join(pools.values())
    remaining = longueur - len(password_chars)
    password_chars += [secrets.choice(all_chars) for _ in range(remaining)]

    # Mélanger de façon sécurisée
    sysrand = random.SystemRandom()
    sysrand.shuffle(password_chars)

    return "".join(password_chars)