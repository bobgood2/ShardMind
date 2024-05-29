import sys
import os
sys.path.append(os.getcwd())
from Config import config
import os
import shutil

def delete_all_files_in_directory(directory):
    if not os.path.exists(directory):
        print(f"The directory {directory} does not exist.")
        return
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file or symbolic link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the directory and all its contents
                print(f"Deleted directory and its contents: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

delete_all_files_in_directory(config.EMAILS_POSTING_LIST_DIR)
delete_all_files_in_directory(config.EMAILS_INDEXED_EMBEDDINGS_DIR)
delete_all_files_in_directory(config.EMAILS_EMBEDDINGS_DIR)
delete_all_files_in_directory(config.EMAILS_METADATA_DIR)
