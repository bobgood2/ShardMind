import os


root = os.getenv('INDEX_ROOT', 'index')  # Default to development if not set

if root != 'index':
    print (f"**** {root} <==  root directory changed ***")
    print (f"**** {root} <==  root directory changed ***")
    print (f"**** {root} <==  root directory changed ***")
    print (f"**** {root} <==  root directory changed ***")
    
EMAILS_RAW_DIR = f'C:\\{root}\\email\\emails'
EMAILS_RAW_DIR2 = f'C:\\{root}\\email\\emails2'  
FILES_RAW_DIR = f'C:\\{root}\\file\\files'
CHATS_RAW_DIR = f'C:\\{root}\\chat\\chats'
CALENDAR_RAW_DIR = f'C:\\{root}\\calendar\\calendar'
PEOPLE_RAW_DIR = f'C:\\{root}\\people\\people'
PARQUET_DIR = f'C:\\{root}\\raw'
EMAILS_MAPPING_FILE = f'C:\\{root}\\email\\index_mappings.json'
EMAILS_INDEXED_EMBEDDINGS_DIR = f'C:\\{root}\\email\\indexed_embeddings'
EMAILS_EMBEDDINGS_DIR = f'C:\\{root}\\email\\embeddings'
CALENDAR_EMBEDDINGS_DIR = f'C:\\{root}\\calendar\\embeddings'
EMAILS_INDEX_FILE = f'C:\\{root}\\email\\index.faiss'
EMAILS_POSTING_LIST_DIR = f'C:\\{root}\\email\\posting_lists'
EMAILS_WHO_FILE = f'C:\\{root}\\email\\who.json'
EMAILS_METADATA_DIR = f'C:\\{root}\\email\\metadata'
EMAILS_WHEN_FILE = f'C:\\{root}\\email\\when.json'
EMAILS_CHECKPOINT_FILE = f'C:\\{root}\\email\\checkpoint.txt'


directories = [
    EMAILS_RAW_DIR,
    EMAILS_RAW_DIR2,
    FILES_RAW_DIR,
    CHATS_RAW_DIR,
    CALENDAR_RAW_DIR,
    PEOPLE_RAW_DIR,
    EMAILS_INDEXED_EMBEDDINGS_DIR,
    EMAILS_EMBEDDINGS_DIR,
    CALENDAR_EMBEDDINGS_DIR,
    EMAILS_POSTING_LIST_DIR,
    EMAILS_METADATA_DIR,
    PARQUET_DIR,
]

# Function to create directories if they do not exist
def ensure_directories_exist(dir_list):
    for directory in dir_list:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

import os

def change_dir_and_ext(file_path, new_dir, new_ext):
    if not os.path.exists(new_dir):
        raise ValueError("directory does not exist")
    
    file_name = os.path.basename(file_path)
    base_name, _ = os.path.splitext(file_name)
    return os.path.join(new_dir, base_name + new_ext)
   

# Ensure all directories exist
ensure_directories_exist(directories)