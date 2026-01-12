import cv2
import numpy as np

cap = cv2.VideoCapture(0)  # 0 = webcam par défaut

frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frames.append(frame)  # frame est déjà un np.array (H, W, 3)

    cv2.imshow("Capture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

video_array = np.array(frames)
for f in video_array:
    print(f)
print(video_array.shape)






