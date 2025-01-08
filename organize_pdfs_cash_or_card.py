import os
import shutil

# Specify the base path where your PDF files are located
base_path = input("Enter the path where your PDF files are located: ")

# Define the target directories
network_folder = os.path.join(base_path, "شبكة")
cache_folder = os.path.join(base_path, "كاش")

# Create the network folder if it doesn't exist
os.makedirs(network_folder, exist_ok=True)

# Check if there are any PDF files with "كاش" in the name
has_cache_files = any("كاش" in filename for filename in os.listdir(base_path) if filename.endswith(".pdf"))

# Create the cache folder only if there are cache files
if has_cache_files:
    os.makedirs(cache_folder, exist_ok=True)

# Iterate over all files in the base path
for filename in os.listdir(base_path):
    if filename.endswith(".pdf"):
        # Check for keywords in the filename
        if "شبكة" in filename:
            shutil.move(os.path.join(base_path, filename), os.path.join(network_folder, filename))
            print(f"Moved {filename} to {network_folder}")
        elif "كاش" in filename and has_cache_files:
            shutil.move(os.path.join(base_path, filename), os.path.join(cache_folder, filename))
            print(f"Moved {filename} to {cache_folder}")

print("Files have been organized.")