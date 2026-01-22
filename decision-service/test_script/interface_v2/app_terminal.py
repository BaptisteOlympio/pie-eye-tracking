import sys
import time
from fake_decision import FakeEyeTracker
from logic_wheel import DecisionWheel

def main():
    # 1. Initialisation
    tracker = FakeEyeTracker()
    
    # On définit le seuil : il faut 20 "ticks" pour valider
    # Avec un sleep de 0.05s, cela fait environ 1 seconde de maintien
    wheel = DecisionWheel(seuil_validation=20)

    print("\n" * 2)
    print("==========================================")
    print("   TEST TERMINAL : LOGIQUE DE LA ROUE")
    print("==========================================")
    print(f"Mode détecté : {tracker.get_mode()}")
    print("-> Maintenez une flèche pour charger la roue.")
    print("-> Relâchez pour annuler.")
    print("-> Ctrl+C pour quitter.")
    print("\n")

    try:
        while True:
            # --- A. Récupération ---
            raw_data = tracker.get_gaze_data()
            current_dir = raw_data['direction']

            # --- B. Traitement Logique ---
            # On envoie la direction brute à la "Roue" qui nous renvoie l'état calculé
            state = wheel.update(current_dir)
            
            # --- C. Affichage "Graphique" dans le Terminal ---
            
            # Récupération des infos utiles
            progress = state['progress']
            limit = state['progress_max']
            percent = state['percent']
            validated_decision = state['validated']
            
            # Création d'une barre de chargement ASCII : [█████-----]
            bar_len = 20
            nb_carres = int(bar_len * (percent / 100))
            bar_visual = "█" * nb_carres + "-" * (bar_len - nb_carres)

            # Gestion du message de statut
            if validated_decision:
                status_msg = f"✅ VALIDÉ : {validated_decision} !!"
            elif current_dir == "CENTER":
                status_msg = "Attente..."
            else:
                status_msg = f"Chargement {current_dir}..."

            # Construction de la ligne d'affichage
            # \r permet de revenir au début de la ligne sans sauter de ligne
            # Cela donne l'impression d'une animation fluide
            output = f"\r[{bar_visual}] {int(percent):>3}% | {status_msg:<25}"
            
            sys.stdout.write(output)
            sys.stdout.flush()

            # Vitesse de la boucle (Simule les FPS)
            time.sleep(0.05) 

    except KeyboardInterrupt:
        # Nettoyage propre en quittant
        if hasattr(tracker, 'terminal_handler'):
            tracker.terminal_handler.stop()
        print("\n\nFin du test.")

if __name__ == "__main__":
    main()