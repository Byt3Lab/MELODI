def jwt_encode(payload, secret_key, algorithm="HS256"):
    import jwt
    return jwt.jwt_encode(payload, secret_key, algorithm=algorithm)

def jwt_decode(token, secret_key, algorithms=["HS256"]):
    import jwt
    try:
        return jwt.jwt_decode(token, secret_key, algorithms=algorithms)
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token