import pandas as pd

if __name__ == "__main__" :
    columns = ["frame",
               "face_id",
               "timestamp",
               "confidence",
               "success",
               "gaze_0_x",
               "gaze_0_y",
               "gaze_0_z",
               "gaze_1_x",
               "gaze_1_y",
               "gaze_1_z",
               "gaze_angle_x",
               "gaze_angle_y"]
    gaze_angle = [
        "gaze_angle_x",
        "gaze_angle_y"
    ]
    
    df = pd.read_csv("/workspace/data/data.csv")
    df_selected = df[gaze_angle]
    print(df_selected.max(), df_selected.min())