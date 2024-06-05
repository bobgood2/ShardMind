from ast_transform import language_client
import asyncio
from datetime import datetime, timedelta
import requests
import json
import uuid
from Orchestrator import app_logging as logging

class MyConversation(language_client.Conversation):
    def __init__(self, client, code, guid):
        super().__init__(client, code)
        self.guid=guid
        self.final=None
        
    def on_new_code(self,value):
        print("on new code: "+value)        
    
    def on_done(self):
        print("on done")        

    def on_exception(self,value):
        print("on exception: "+value)        
    
    def on_return(self,value):
        self.final = str(value)
        print("on return: "+str(value))        
    
    def on_complete(self):
        print("on complete ")        
    
    @language_client.managed_function
    def search_email(self, text=None, sender=None, fromWho=None, toRecipients=None, ccRecipients=None, bccRecipients=None, replyTo=None, after=None, before=None, take=None):
        email_params = {
            'text': text,
            'sender': sender,
            'from': fromWho,
            'toRecipients': toRecipients,
            'ccRecipients': ccRecipients,
            'bccRecipients': bccRecipients,
            'replyTo': replyTo,
            'after': after,
            'before': before,
            'take': take
        }

        # Filter out None values
        filtered_params = {k: v for k, v in email_params.items() if v is not None}
        url = "http://127.0.0.1:5001/search_email"
        headers = {
            "Content-Type": "application/json"
        }

        start_time= datetime.now()
        start_stamp=logging.thenstamp(start_time)

        response = requests.post(url, headers=headers, data=json.dumps(filtered_params))

        end_time=datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        self.final = response.json()
        logging.log(
            {'guid': self.guid,
             'title': 'search_email',
             'timestamp': start_stamp,
             'duration': elapsed_time,
             'parameters': str(filtered_params),
             'output': response.json()
             })


     
    @language_client.managed_function
    def search_teams(self, a=0, b=0, c=0):
        return a+100
    
    @language_client.managed_function
    def search_meetings(self, a=0, b=0, c=0):
        return a+100
    
    @language_client.managed_function
    def wrap_string(self, a=0, b=0, c=0):
        return a+100

class PlanRunner:
    def __init__(self):
        self.config = {'module_blacklist':['io']}
        self.client = language_client.ApiConductorClient(self.config, MyConversation)
    
    async def Run(self, code, guid):
        conversation = MyConversation(self, code, guid)
        await conversation.task
        return conversation
        
    def Close(self):
        self.client.close()

if __name__ == '__main__':
    async def main():
        config = {'module_blacklist':['io']}

        client = language_client.ApiConductorClient(config, MyConversation)
        guid= str(uuid.uuid4())
        src = """
a=search_email(text="hi")
return a
"""
        conversation = MyConversation(client, src, guid)
        await conversation.task

        client.close()
        
    asyncio.run(main())
