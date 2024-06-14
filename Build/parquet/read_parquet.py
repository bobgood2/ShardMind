import os
import pandas as pd
import numpy as np
import json
import datetime
from Config import config
def find_parquet_files(directory):
    parts = split_path(directory)
    group = parts[-1]
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            find_parquet_files(full_path)
        elif full_path.endswith('.parquet'):
            read_parquet_file(full_path, group)
             
def read_parquet_file(full_path, group):
    if group=="document":
        read_parquet(full_path, config.FILES_RAW_DIR)
    elif group=="mail":
        read_parquet(full_path, config.EMAILS_RAW_DIR2)
    elif group=="teamsconversation":
        read_parquet(full_path, config.CHATS_RAW_DIR)
    elif group=="people":
        read_parquet(full_path, config.PEOPLE_RAW_DIR)
    elif group=="calendar":
        read_parquet(full_path, config.CALENDAR_RAW_DIR)
 
bad=0 
file_cnt=0
def read_parquet(full_path, output_dir):
    global bad, file_cnt
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_parquet(full_path, engine='pyarrow')
    if df.empty:
        bad+=1
        return
    
    file_cnt+=1
    if file_cnt%100==0:
        print(file_cnt)
    
    data_objects = [DataRow(**row.to_dict()) for index, row in df.iterrows()]
        
    # Print the list of DataRow objects
    for obj in data_objects:
        if not obj.is_empty():
            filename = os.path.join(output_dir, f"{obj.Id}.json")
            try:
                if not os.path.exists(filename):
                    with open(filename, 'w') as json_file:
                        json.dump(obj.to_dict(), json_file, indent=4, cls=CustomEncoder)
            except:
                pass

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp) or isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            try:
                return obj.decode('utf-8')  # Attempt to decode using UTF-8
            except UnicodeDecodeError:
                return obj.decode('latin-1')  # Fallback to a different encoding if necessary
        elif isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert numpy array to list
        # Add more type checks as needed
        t = o.__class__.__name__
        return super().default(obj)
    
class DataRow:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"DataRow({', '.join(f'{key}={value}' for key, value in self.__dict__.items())})"

    def to_dict(self):
        return self.__dict__

    def is_empty(self):
        if hasattr(self, 'FileSize'):
            return self.FileSize <= 0
        elif hasattr(self, 'DisplayName'):           
            return len(self.DisplayName) == 0       
        elif hasattr(self, 'Organizer'):           
            return not self.Organizer       
        elif hasattr(self, 'From'):           
            return not self.From       
        else:
            pass
    
def split_path(path):
    parts = []
    while True:
        path, tail = os.path.split(path)
        if tail:
            parts.append(tail)
        else:
            if path:
                parts.append(path)
            break
    parts.reverse()
    return parts


# Example usage
directory = config.PARQUET_DIR
find_parquet_files(directory)
