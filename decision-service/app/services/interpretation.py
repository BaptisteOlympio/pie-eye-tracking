
async def get_direction_from_gaze(gaze) :
    # Plages réelles observées
    # X: -0.2 (gauche, vers -1) à -0.16 (droite, vers +1)
    # Y: -0.1 (haut, vers -1) à 0.03 (bas, vers +1)
    gaze_min_x = -0.13  # Gauche
    gaze_max_x = 0.18  # Droite
    gaze_min_y = 0.02  # Haut
    gaze_max_y = 0.23   # Bas

    gaze_center_x = (gaze_max_x + gaze_min_x) / 2  # -0.18
    gaze_center_y = (gaze_max_y + gaze_min_y) / 2  # -0.035

    gaze_x = gaze[0]
    gaze_y = gaze[1]

    # Seuil adapté aux vraies plages (30% de la plage)
    threshold_x = (gaze_max_x - gaze_min_x) * 0.3  # ~0.012
    threshold_y = (gaze_max_y - gaze_min_y) * 0.3  # ~0.039

    # Si on est au centre sur les deux axes
    if abs(gaze_x - gaze_center_x) < threshold_x and abs(gaze_y - gaze_center_y) < threshold_y:
        return "CENTER"
    
    # Déterminer la direction dominante (normalisée)
    x_distance = abs(gaze_x - gaze_center_x) / ((gaze_max_x - gaze_min_x) / 2)
    y_distance = abs(gaze_y - gaze_center_y) / ((gaze_max_y - gaze_min_y) / 2)
    
    if x_distance >= y_distance:
        # Direction horizontale dominante
        if gaze_x - gaze_center_x > 0:
            return "RIGHT"  # Vers x positif (+1)
        else:
            return "LEFT"   # Vers x négatif (-1)
    else:
        # Direction verticale dominante
        if gaze_y - gaze_center_y > 0:
            return "DOWN"   # Vers y positif (+1)
        else:
            return "UP"     # Vers y négatif (-1)