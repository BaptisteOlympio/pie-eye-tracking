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
    
    df = pd.read_csv("/workspace/data/data.csv")
    last_row = df.tail(1)
    selected_last_row = last_row[columns]
    print(selected_last_row.to_dict("records"))