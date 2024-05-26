import os
from datetime import datetime

def get_directory_info(directory_path):
    num_files = 0
    latest_time = None
    
    for root, dirs, files in os.walk(directory_path):
        num_files += len(files)
        
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = os.path.getmtime(file_path)
            if latest_time is None or file_mtime > latest_time:
                latest_time = file_mtime

    latest_time = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %I:%M %p') if latest_time else None
    return num_files, latest_time

dirs=['C:\download\emails','C:\download\emails_metadata','C:\download\emails_embeddings']

# Replace 'your_directory_path' with the path to the directory you want to check
directory_path = 'your_directory_path'

for directory_path in dirs:
	
	num_files, latest_time = get_directory_info(directory_path)
	print(f"{directory_path}: {num_files}  {latest_time}")
