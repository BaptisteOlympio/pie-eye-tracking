class DecisionWheel:
    def __init__(self, seuil_validation=4):
        self.seuil = seuil_validation  # Nombre de "ticks" pour valider
        self.compteur = 0             # Où on en est (ex: 2/4)
        self.direction_en_cours = "CENTER"
        self.decision_validee = None  # Stockera la décision finale (ex: "UP") une fois validée

    def update(self, raw_input_direction):
        """
        Reçoit la direction brute du clavier (fake_decision)
        Retourne un dictionnaire avec l'état de la roue.
        """
        
        # 1. Si l'utilisateur regarde au CENTRE (il ne fait rien)
        if raw_input_direction == "CENTER":
            self.compteur = 0
            self.direction_en_cours = "CENTER"
            self.decision_validee = None
            
        # 2. Si l'utilisateur continue dans la MÊME direction
        elif raw_input_direction == self.direction_en_cours:
            if self.compteur < self.seuil:
                self.compteur += 1
            
            # Si on atteint le seuil, on valide !
            if self.compteur >= self.seuil:
                self.decision_validee = raw_input_direction

        # 3. Si l'utilisateur CHANGE de direction
        else:
            # On remet le compteur à 1 pour la nouvelle direction
            self.direction_en_cours = raw_input_direction
            self.compteur = 1
            self.decision_validee = None

        # On renvoie les infos pour l'interface graphique
        return {
            "direction": self.direction_en_cours,
            "progress": self.compteur,         # Ex: 2
            "progress_max": self.seuil,        # Ex: 4
            "percent": (self.compteur / self.seuil) * 100, # Ex: 50%
            "validated": self.decision_validee # Ex: "UP" ou None
        }


