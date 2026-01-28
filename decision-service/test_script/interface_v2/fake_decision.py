class FakeListDriver:
    """
    Simule un Eye-Tracker avec un scénario complexe pour tester
    la résilience (Buffer) et la validation.
    """
    def __init__(self):
        # SCÉNARIO DE TEST COMPLET (pour Seuil=4 et Buffer=2)
        self.scenario = [
            # --- PHASE 1 : CALIBRATION ---
            "CENTER", "CENTER", "CENTER",
            
            # --- PHASE 2 : SUCCÈS SIMPLE (DROITE) ---
            # On regarde à droite en continu -> Ça doit valider (OK)
            "RIGHT", "RIGHT", "RIGHT", "RIGHT", 
            "RIGHT", # Maintien (reste validé)
            "CENTER", "CENTER", # Retour au calme
            
            # --- PHASE 3 : TEST DU BUFFER (RÉSILIENCE HAUT) ---
            # L'utilisateur regarde HAUT, cligne des yeux (CENTER), puis revient
            "UP", "UP",           # 50%
            "CENTER",             # Oups ! (Buffer activé : HAUT reste figé à 50%)
            "UP",                 # Retour ! (Reprise : 75%)
            "UP",                 # (Validation : 100%)
            "UP",                 # Maintien
            "CENTER", "CENTER",
            
            # --- PHASE 4 : TEST D'ABANDON (ÉCHEC GAUCHE) ---
            # L'utilisateur commence GAUCHE, puis regarde ailleurs trop longtemps
            "LEFT", "LEFT", "LEFT", # 75%
            "CENTER",               # Pause (Buffer 1/2)
            "CENTER",               # Pause (Buffer 2/2)
            "CENTER",               # Trop long ! (Reset -> GAUCHE disparaît)
            "CENTER",               # On est bien revenu à zéro
            
            # --- PHASE 5 : CHANGEMENT D'AVIS (CONFLIT BAS -> DROITE) ---
            # L'utilisateur regarde BAS, puis change brusquement pour DROITE
            "DOWN", "DOWN",       # BAS 50%
            "RIGHT",              # Input DROITE arrive...
                                  # ...Mais BAS est en mémoire ! (Buffer BAS 1/2)
            "RIGHT",              # Input DROITE... (Buffer BAS 2/2)
            "RIGHT",              # Buffer BAS dépassé -> BAS annulé, DROITE commence (25%)
            "RIGHT", "RIGHT", "RIGHT", # Validation DROITE
            
            # --- PHASE 6 : FIN ---
            "CENTER", "CENTER", "CENTER"
        ]
        self.index = 0

    def get_next_direction(self):
        current_val = self.scenario[self.index]
        self.index = (self.index + 1) % len(self.scenario)
        return current_val