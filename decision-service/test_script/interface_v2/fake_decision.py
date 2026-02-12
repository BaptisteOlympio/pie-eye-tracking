class FakeListDriver:
    """
    Simule un scénario Domotique complet :
    1. Attente (Menu Principal visible)
    2. Sélection du SALON
    3. Allumage de la lumière
    4. Changement vers les Volets
    5. Ouverture des Volets
    """
    def __init__(self):
        # Rappel : Il faut 4 "UP" pour valider une action (100%)
        # On ajoute souvent un 5ème pour simuler le maintien naturel du regard
        
        self.scenario = [
            # --- DÉPART : PAUSE (3 secondes environ) ---
            # Permet à l'interface de charger et d'afficher le MENU PRINCIPAL
            "CENTER", "CENTER", "CENTER", "CENTER", 
            "CENTER", "CENTER", "CENTER", "CENTER",
            
            # --- ACTION 1 : CHOISIR "SALON" (HAUT) ---
            # On est dans le Menu Principal
            "UP", "UP", "UP", "UP",   # 25% -> 50% -> 75% -> 100% (Validé !)
            "UP",                     # Maintien
            "CENTER", "CENTER",       # Relâchement (Retour au calme)
            
            # (À ce stade, l'interface affiche le SALON et la LUMIÈRE)
            
            # --- PAUSE D'OBSERVATION ---
            "CENTER", "CENTER", "CENTER", "CENTER",
            
            # --- ACTION 2 : ALLUMER LA LUMIÈRE (HAUT) ---
            # Le bouton HAUT affiche "ALLUMER"
            "UP", "UP", "UP", "UP",   # Validation
            "UP",                     # Maintien
            "CENTER", "CENTER",       # Relâchement
            
            # (La lumière est ON. Le bouton HAUT devient vide, BAS devient ÉTEINDRE)
            
            # --- PAUSE ---
            "CENTER", "CENTER",
            
            # --- ACTION 3 : PASSER AU VOLET (DROITE / SUIVANT) ---
            "RIGHT", "RIGHT", "RIGHT", "RIGHT", # Validation
            "RIGHT",
            "CENTER", "CENTER",
            
            # (L'écran affiche maintenant "Volets")
            
            # --- ACTION 4 : MONTER LE VOLET (HAUT / +) ---
            "UP", "UP", "UP", "UP",   # Validation (+10%)
            "UP",
            "CENTER", "CENTER",
            
            # --- FIN DU SCÉNARIO ---
            # On reste au centre pour observer le résultat
            "CENTER", "CENTER", "CENTER", "CENTER", "CENTER"
        ]
        self.index = 0

    def get_next_direction(self):
        """
        Retourne la direction suivante et boucle à la fin.
        """
        current_val = self.scenario[self.index]
        self.index = (self.index + 1) % len(self.scenario)
        return current_val