import os
from core.utils.file_permissions import FilePermissions

def test_creation_avec_permissions(dossier_nom="dossier_test", fichier_nom="fichier_test.txt"):
    """
    Tente de créer un dossier et un fichier à l'intérieur.
    Si une erreur de permission survient, utilise FilePermissions pour accorder 
    les droits en écriture et réessaie.
    """
    chemin_dossier = os.path.abspath(dossier_nom)
    chemin_fichier = os.path.join(chemin_dossier, fichier_nom)
    
    print(f"-> Tentative initiale (Dossier: '{dossier_nom}', Fichier: '{fichier_nom}')")
    try:
        # Tente de créer le dossier s'il n'existe pas
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)
        
        # Tente de créer le fichier
        with open(chemin_fichier, "w", encoding="utf-8") as f:
            f.write("Contenu du fichier test initial")
        print("Succès : Le dossier et le fichier ont été créés sans problème de permission.")
        
    except PermissionError:
        print("Erreur : PermissionError interceptée. Le programme va tenter d'accorder les droits...")
        
        # Cas 1 : Le dossier a été créé précédemment mais on n'a pas les droits pour écrire dedans
        if os.path.exists(chemin_dossier):
            fp = FilePermissions(chemin_dossier)
            print(f"1) Permissions actuelles sur '{dossier_nom}': {fp.check_permissions()}")
            
            # Ajout des droits (lecture, écriture, exécution)
            print("2) Attribution des droits de lecture/écriture/exécution...")
            fp.set_permissions({"read": True, "write": True, "execute": True})
            
            # Vérification des nouveaux droits
            print(f"3) Nouvelles permissions sur '{dossier_nom}': {fp.check_permissions()}")
            
            # Réessayer
            print("-> Deuxième tentative de création du fichier...")
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write("L'écriture a réussi après la résolution des permissions !")
            print("Succès : Le fichier a été créé et écrit après avoir accordé les droits.")
            
        # Cas 2 : Le dossier n'a même pas pu être créé (problème sur le dossier parent)
        else:
            dossier_parent = os.path.dirname(chemin_dossier)
            print(f"1) Problème sur le dossier parent : {dossier_parent}")
            fp_parent = FilePermissions(dossier_parent)
            
            # Ajout des droits sur le parent
            print("2) Attribution des droits sur le dossier parent...")
            fp_parent.set_permissions({"read": True, "write": True, "execute": True})
            
            # Réessayer de créer le dossier
            os.makedirs(chemin_dossier)
            
            # Réessayer de créer le fichier
            print("-> Deuxième tentative de création du fichier...")
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write("L'écriture a réussi après la résolution des permissions du dossier parent !")
            print("Succès : Le fichier a été créé après avoir accordé les droits au dossier parent.")

fp = FilePermissions("modules")
print(fp.check_permissions())

if __name__ == "__main__d":
    dossier_simulation = "simulation_permissions"
    fichier_simulation = "resultat.txt"
    
    print("=== DÉBUT DU TEST DE FILE_PERMISSIONS ===\n")
    
    # ---------------------------------------------------------
    # PARTIE 1 : Préparation pour forcer l'erreur
    # ---------------------------------------------------------
    print("--- Préparation de l'environnement (simulation de l'erreur) ---")
    if not os.path.exists(dossier_simulation):
        os.makedirs(dossier_simulation)
        
    fp_sim = FilePermissions(dossier_simulation)
    print(f"Dossier '{dossier_simulation}' créé.")
    
    print("Permissions actuelles sur le dossier :")
    print(fp_sim.check_permissions())
    # On retire explicitement les droits d'écriture pour forcer une PermissionError
    # lors de la création du fichier à l'intérieur
    print("Retrait des droits d'écriture sur le dossier...")
    fp_sim.set_permissions({"read": True, "write": False, "execute": True})
    
    print("\n--- Lancement de la fonction de test ---")
    # ---------------------------------------------------------
    # PARTIE 2 : Appel de la fonction de test demandée
    # ---------------------------------------------------------
    test_creation_avec_permissions(dossier_simulation, fichier_simulation)
    
    print("\n=== FIN DU TEST ===")
