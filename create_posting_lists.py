import json
import os

from numpy import frombuffer

# Path to the JSON file
mapping_file_path = r'C:\download\email_index_mappings'

# Read the sorted filenames from the JSON file
with open(mapping_file_path, 'r') as f:
    sorted_filenames = json.load(f)

emails_dir = 'C:\download\emails_metadata'
posting_list_dir = 'C:\download\email_posting_lists'

posting_lists = {}
when_list = []

def postWho(prefix, who, index):
    token = (prefix, who[0], who[1])
    if token not in posting_lists:
        posting_lists[token]=set([])
    posting_lists[token].add(index)

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
        with open(os.path.join(emails_dir, new_filename), 'r') as f:
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

posting_list_dir = 'C:\download\email_posting_lists'

with open(os.path.join(posting_list_dir,"when.json"), 'w') as f:
    json.dump(when_list, f)

import re

def sanitize_filename(input_tuple, max_length=250):
    # Combine the tuple elements into a single string
    combined_string = "_".join(input_tuple)
    
    # Define a regular expression pattern to match illegal filename characters
    illegal_chars_pattern = r'[<>:"/\\|?*()@\' ]'
    
    # Replace illegal characters with an underscore
    sanitized_string = re.sub(illegal_chars_pattern, '_', combined_string)
    
    # Truncate the string if it's longer than the maximum allowed length
    if len(sanitized_string) > max_length:
        sanitized_string = sanitized_string[:max_length]
    
    # Add the .json extension
    filename = sanitized_string + ".json"
    
    return filename

for poster in posting_lists.keys():
    fn = os.path.join(posting_list_dir, sanitize_filename(poster))
    try:
        with open(fn, 'w') as f:
            data = {"token": poster, "posting_list": list(posting_lists[poster])}
            json.dump(data, f)
    except Exception as e:
        print(f"could not write {fn} {e}")
        pass


        