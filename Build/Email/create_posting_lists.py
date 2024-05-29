import sys
import os
sys.path.append(os.getcwd())
import json
from Config import config
import traceback

from numpy import frombuffer

# create_posting_list depends on index_build because it reads the 
# mappings file (i.e. id assignment per objet)
# populates the posting list directory
# also creates the when file, since Ids are sorted by age

# Read the sorted filenames from the JSON file
with open(config.EMAILS_MAPPING_FILE, 'r') as f:
    sorted_filenames = json.load(f)

posting_lists = {}
when_list = []

def postWho(prefix, who, index):
    if who==None:
        return
    try:
        token = (prefix, who[0], who[1])
        if token not in posting_lists:
            posting_lists[token]=set([])
        posting_lists[token].add(index)
    except Exception as e:
        stack_trace = traceback.format_exc()
        print(f"exception {e} {stack_trace}")

def postBool(prefix, val, index):
    if val:
        token = prefix
        if token not in posting_lists:
            posting_lists[token]=set([])
        posting_lists[token].add(index)
        
for index in range(len(sorted_filenames)):
    if index>0 and index%100 ==0:
        print(index)
    fn = sorted_filenames[index]
    root, ext = os.path.splitext(fn)
    new_filename = root + ".json"
    try:
        with open(os.path.join(config.EMAILS_METADATA_DIR, new_filename), 'r') as f:
            metadata = json.load(f)
            when = metadata['receivedDateTime']
            when_list.append(when)
            postWho("from",metadata["from"], index)
            postWho("sender",metadata["sender"], index)
            for toRecipients in metadata["toRecipients"]:
                postWho("toRecipients", toRecipients, index)
            for ccRecipients in metadata["ccRecipients"]:
                postWho("ccRecipients", ccRecipients, index)
            for bccRecipients in metadata["bccRecipients"]:
                postWho("bccRecipients", bccRecipients, index)
            for replyTo in metadata["replyTo"]:
                postWho("replyTo", replyTo, index)
            postBool("isRead", metadata["isRead"], index)
            postBool("isDraft", metadata["isDraft"], index)
            postBool("hasAttachments", metadata["hasAttachments"], index)
    except:
        pass

with open(config.EMAILS_WHEN_FILE, 'w') as f:
    json.dump(when_list, f)

import re

def sanitize_filename(input_tuple, max_length=250):
    # Combine the tuple elements into a single string
    combined_string = "_".join(input_tuple)
    
    # Define a regular expression pattern to match illegal filename characters
    illegal_chars_pattern = r'[<>:"/\\|?*()@\' \x00-\x1F]'
    
    # Replace illegal characters with an underscore
    sanitized_string = re.sub(illegal_chars_pattern, '_', combined_string)
    
    # Truncate the string if it's longer than the maximum allowed length
    if len(sanitized_string) > max_length:
        sanitized_string = sanitized_string[:max_length]
    
    # Add the .json extension
    filename = sanitized_string + ".json"
    
    return filename

print("writing files")
for poster in posting_lists.keys():
    fn = os.path.join(config.EMAILS_POSTING_LIST_DIR, sanitize_filename(poster))
    try:
        with open(fn, 'w') as f:
            data = {"token": poster, "posting_list": list(posting_lists[poster])}
            json.dump(data, f)
    except Exception as e:
        print(f"could not write {fn} {e}")
        pass


        