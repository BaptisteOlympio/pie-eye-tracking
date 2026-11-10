from collections import deque
import numpy as np

# On fait un queue pour stocker les dernier regards

taille_fenetre = 5
array_nan = np.zeros(2)
array_nan.fill(np.nan)
# print(array_nan)

x = deque(taille_fenetre * [array_nan], taille_fenetre)


for i in range(1, 10):
    x.append(np.array([i, i]))
    # print(x)

# On fait notre prédiction

data = np.stack(list(x))
data = np.array([[-1, 0], [-1, 0]])
print("Shape de la data :", data.shape)


def decision(data):
    """
    Test méthode de decision, on vérifie
    """
    threhlod_x_gauche = 0
    threhlod_x_droite = 0
    threhlod_y_haut = 0
    threhlod_y_bas = 0

    zone_gauche = (data[:, 0] < threhlod_x_gauche).all()
    zone_droite = (data[:, 0] > threhlod_x_droite).all()
    return


decision(data=data)
