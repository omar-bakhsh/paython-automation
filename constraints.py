import os
from datetime import datetime

# Specify the base path where you want to create the folder
base_path = input("Enter the path where you want to create the folder: ")  # User input for path

# Get the current day, month, and year
current_day = datetime.now().strftime("%d")
current_month = datetime.now().strftime("%m")
current_year = datetime.now().strftime("%Y")

# Create a formatted folder name
folder_name = f"{current_day}-{current_month}-{current_year}"

# Create the full path for the new folder
folder_path = os.path.join(base_path, folder_name)

# Create the folder if it doesn't exist
try:
    os.makedirs(folder_path, exist_ok=True)
    print(f"Folder created: {folder_path}")
except Exception as e:
    print(f"An error occurred: {e}")

# Logging the activity
with open(os.path.join(base_path, "activity_log.txt"), "a") as log_file:
    log_file.write(f"Folder created: {folder_path} at {datetime.now()}\n")