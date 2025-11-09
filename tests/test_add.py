def parse_module_name(requirement: str) -> dict:
    """
    Analyse une chaîne comme 'stock>=1.0.0,==2.2.2' ou 'users==1.2' ou 'compta'
    et retourne :
    {
        "name": "stock",
        "constraints": [
            { "operator": ">=", "version": "1.0.0" },
            { "operator": "==", "version": "2.2.2" }
        ]
    }
    """

    import re

    # Regex pour capturer le nom et les contraintes
    pattern = r"^([a-zA-Z0-9_\-]+)((?:[=<>!]+[\d\.]+(?:,)?)+)?$"
    match = re.match(pattern, requirement.strip())

    if not match:
        raise ValueError(f"Format invalide : {requirement}")

    name = match.group(1)
    constraints_str = match.group(2)

    constraints = []
    if constraints_str:
        # Trouver toutes les paires (opérateur, version)
        sub_pattern = r"([=<>!]+)\s*([\d\.]+)"
        for op, ver in re.findall(sub_pattern, constraints_str):
            constraints.append({
                "operator": op,
                "version": ver
            })

    return {
        "name": name,
        "constraints": constraints
    }