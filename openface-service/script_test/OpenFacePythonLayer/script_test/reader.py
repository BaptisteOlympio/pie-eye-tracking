import pandas as pd

if __name__ == "__main__" :
    columns = ["frame",
               "gaze_angle_x",
               "gaze_angle_y"]
    gaze_angle = [
        "gaze_angle_x",
        "gaze_angle_y"
    ]
    
    df = pd.read_csv("/workspace/data/data.csv")
    print(len(df.index))
    print(df[columns].loc[0].to_dict())