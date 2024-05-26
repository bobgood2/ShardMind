import os
from datetime import datetime
import json

email_dir="C:\download\emails"
def get_age(file_path):
    try:
        fp=email_dir+"\\"+file_path
        with open(fp, 'r') as file:
            metadata = json.load(file)
    except:
        return 0    
    time_string = metadata["receivedDateTime"]
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    given_time = datetime.strptime(time_string, time_format)
    age = (datetime.now() - given_time).total_seconds()
    last_age = age/3600/24/365 
    return last_age

def get_directory_info(directory_path):
    num_files = 0
    latest_time = None
    last_file=None
    
    for root, dirs, files in os.walk(directory_path):
        num_files += len(files)
        
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = os.path.getmtime(file_path)
            if latest_time is None or file_mtime > latest_time:
                latest_time = file_mtime
                last_file=file

    latest_time = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %I:%M %p') if latest_time else None
    return num_files, latest_time, get_age(last_file)

dirs=['C:\download\emails','C:\download\emails_metadata','C:\download\emails_embeddings']

# Replace 'your_directory_path' with the path to the directory you want to check
directory_path = 'your_directory_path'

for directory_path in dirs:
	
	num_files, latest_time, age = get_directory_info(directory_path)
	print(f"{directory_path}: {num_files}  {latest_time} {age} years")
