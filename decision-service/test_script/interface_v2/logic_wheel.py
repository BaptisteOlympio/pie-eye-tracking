class DecisionWheel:
    def __init__(self, seuil_validation=4, buffer_limit=2):
        self.seuil = seuil_validation      # Ex: 4 ticks pour 100%
        self.buffer_limit = buffer_limit   # Ex: 2 ticks de tolérance
        
        self.compteur = 0
        self.buffer_compteur = 0
        self.direction_en_cours = "CENTER"
        self.decision_validee = None

    def update(self, raw_input_direction):
        """
        Logique de Résilience Totale :
        Si on a commencé quelque chose, on ne l'annule JAMAIS tout de suite.
        On utilise toujours le buffer.
        """
        
        # 1. EST-CE QU'ON CONTINUE DANS LA MÊME DIRECTION ?
        if raw_input_direction == self.direction_en_cours:
            # Oui -> Tout va bien, on reset le stress (buffer)
            self.buffer_compteur = 0
            
            # On continue de remplir (si ce n'est pas le centre)
            if self.direction_en_cours != "CENTER":
                if self.compteur < self.seuil:
                    self.compteur += 1
                
                # Validation ?
                if self.compteur >= self.seuil:
                    self.decision_validee = self.direction_en_cours

        # 2. NON, LE REGARD A CHANGÉ (Centre, autre direction, erreur...)
        else:
            # Est-ce qu'on avait du progrès à protéger ?
            if self.compteur > 0:
                # OUI -> ON ACTIVE LE BUFFER (PROTECTION)
                self.buffer_compteur += 1
                
                # Tant qu'on est dans la tolérance, ON NE BOUGE PAS.
                # On ignore le nouvel input, on garde l'ancienne direction figée.
                if self.buffer_compteur <= self.buffer_limit:
                    pass # On est en PAUSE
                
                # Si on a dépassé la tolérance, c'est perdu.
                else:
                    self._switch_direction(raw_input_direction)
            
            # Non, on était déjà à 0 (Centre)
            else:
                # Alors on peut changer tout de suite (c'est un nouveau démarrage)
                self._switch_direction(raw_input_direction)

        # Calcul du pourcentage pour l'affichage
        percent = 0
        if self.seuil > 0:
            percent = (self.compteur / self.seuil) * 100

        # On retourne l'état
        return {
            "direction": self.direction_en_cours, # On renvoie ce qu'on a en mémoire (pas forcément l'input)
            "percent": percent,
            "validated": self.decision_validee,
            # Info utile : Est-ce qu'on est en train d'utiliser le buffer ?
            "status": "PAUSE" if (self.buffer_compteur > 0 and self.compteur > 0) else "RUNNING"
        }

    def _switch_direction(self, new_dir):
        """Réinitialisation propre"""
        self.direction_en_cours = new_dir
        self.buffer_compteur = 0
        self.decision_validee = None
        
        # Si on regarde ailleurs que le centre, on commence direct à 1 (25%)
        # Sinon on se met à 0
        if new_dir != "CENTER":
            self.compteur = 1
        else:
            self.compteur = 0