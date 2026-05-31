#!/usr/bin/env python3
from core import Application as Melodi

def get_local_ip():
    import socket

    # On crée un socket UDP (pas besoin de connexion réelle)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # On tente de se connecter à une IP externe (Google DNS : 8.8.8.8)
        # Cela ne génère pas de trafic, cela demande juste au système quelle interface est utilisée
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        # Solution de secours si la méthode précédente échoue
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

app = Melodi()

if __name__ == "__main__":
    port = 5000
    print(f"Votre adresse IP locale est : http://{get_local_ip()}:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
else:
    app = app.get_server()

    