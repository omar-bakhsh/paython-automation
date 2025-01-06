import os
from datetime import datetime

# Specify the path where you want to create the folder  C:\Users\Dell\OneDrive\Desktop\شهر -1\دخل اليومي
base_path = "C:\Users/Dell/OneDrive/Desktop/شهر -1/دخل اليومي"  # Change this to your desired path

# Get the current day
current_day = datetime.now().strftime("%d")  # Get the day as a string (e.g., "22")

# Create the full path for the new folder
folder_path = os.path.join(base_path, current_day)

# Create the folder if it doesn't exist
os.makedirs(folder_path, exist_ok=True)

print(f"Folder created: {folder_path}")