import pandas as pd

df = pd.read_csv("/workspace/data/data.csv")

columns = ["gaze_angle_x", "gaze_angle_y"]


print(df.max()["gaze_angle_x"])