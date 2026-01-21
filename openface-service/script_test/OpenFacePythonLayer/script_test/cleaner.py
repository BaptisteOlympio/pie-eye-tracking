import time
from collections import deque

file_path = "../data/data.csv"
buffer_size = 50
sleep_time = 1  # seconds between each cleanup

while True:
    try:
        # Read last 50 lines
        with open(file_path, "r") as f:
            last_lines = deque(f, maxlen=buffer_size)

        # Write them back
        with open(file_path, "w") as f:
            f.writelines(last_lines)
    except Exception as e:
        print(f"Error processing file: {e}")

    time.sleep(sleep_time)

