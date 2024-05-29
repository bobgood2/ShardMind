email_dir="C:\download\emails"
import json
def get_age(file_path):
    try:
        fp=email_dir+"\\"+file_path
        with open(fp, 'r') as file:
            src = json.load(file)
    except:
        return 0    
    
    metadata={}
    time_string = get_name_addr(src["from"])
    metadata["from"] = get_name_addr(src["from"])
    metadata["toRecipients"]=[get_name_addr(item) for item in src["toRecipients"]]
    metadata["ccRecipients"]=[get_name_addr(item) for item in src["ccRecipients"]]
    metadata["bccRecipients"]=[get_name_addr(item) for item in src["bccRecipients"]]
    metadata["replyTo"]=[get_name_addr(item) for item in src["replyTo"]]
    metadata["isRead"]=src["isRead"]
    metadata["isDraft"]=src["isDraft"]
    metadata["hasAttachments"]=src["hasAttachments"]
    pass

def get_name_addr(item):
    return item["emailAddress"]["name"], item["emailAddress"]["address"]
    

#    "from": {
#        "emailAddress": {
#            "name": "David Ku",
#            "address": "davidku@microsoft.com"
#        }
#    },
#    "toRecipients": [
#        {
#            "emailAddress": {
#                "name": "ASG Shared Platform FTE's",
#                "address": "ASGSPALL@microsoft.com"
#            }
#        }
#    ],
#    "ccRecipients": [
#        {
#            "emailAddress": {
#                "name": "IPG LT",
#                "address": "IPGLT@microsoft.com"
#            }
#        }
#    ],
#    "bccRecipients": [],
#    "replyTo": [],
#    "flag": {
#        "flagStatus": "notFlagged"

get_age("AAMkAGNjYjZlNmUxLWIzNGYtNDc3Ni04YTI3LTcwODFjOGZkMzkwMABGAAAAAABxT_rxjLfGQoiJhM1u-etjBwBlLqkxdm26QJmVjZdJ5nCIAAAAfGyrAAAodlP4a6HZQo2G3v6Cd4flAAADlwGfAAA=.json")
