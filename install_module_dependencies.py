import os
import subprocess
import sys
from pathlib import Path

def join_paths(*paths: str) -> str:
    return os.path.join(*paths)

def path_exist(*paths: str):
    return os.path.exists(*paths)

def create_dir(path_dir, parents=True, exist_ok=True):
    Path(path_dir).mkdir(parents, exist_ok)

def install_module_dependencies():
    """
    Parcourt tous les modules et installe leurs dépendances dans un dossier 'vendor' local.
    """
    # Chemin racine du projet
    BASE_DIR = Path(__file__).resolve().parent
    MODULES_DIR = BASE_DIR / "modules"

    if not MODULES_DIR.exists():
        print(f"❌ Le dossier modules n'existe pas : {MODULES_DIR}")
        return

    print(f"🔍 Recherche de modules dans : {MODULES_DIR}")

    # Parcourir les dossiers dans modules/
    for module_path in MODULES_DIR.iterdir():
        if not module_path.is_dir() or module_path.name.startswith(".") or module_path.name.startswith("_"):
            continue

        requirements_file = join_paths(module_path, "requirements.txt")
        vendor_dir = join_paths(module_path, "vendor")


        if path_exist(requirements_file):
            print(f"📦 Module '{module_path.name}' : requirements.txt trouvé.")
            
            # Créer le dossier vendor s'il n'existe pas
            if not path_exist(vendor_dir):
                create_dir(vendor_dir)
                print(f"   - Dossier 'vendor' créé.")

            print(f"   - Installation des dépendances...")
            
            try:
                # Commande pip install -r requirements.txt -t vendor
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "-r", str(requirements_file), 
                    "-t", str(vendor_dir)
                ])
                print(f"✅ Module '{module_path.name}' : Dépendances installées avec succès.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Module '{module_path.name}' : Erreur lors de l'installation ({e})")
        else:
            print(f"ℹ️  Module '{module_path.name}' : Pas de requirements.txt (ignoré).")

if __name__ == "__main__":
    print("🚀 Démarrage de l'installation des dépendances des modules...")
    install_module_dependencies()
    print("👋 Terminé.")
