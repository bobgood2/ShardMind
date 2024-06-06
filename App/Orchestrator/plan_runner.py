from ast_transform import language_client
import asyncio
from datetime import datetime, timedelta
import requests
import json
import uuid
import traceback
from Orchestrator import app_logging as logging

class MyConversation(language_client.Conversation):
    def __init__(self, client, code, guid):
        print("__init__")
        super().__init__(client, code)
        self.guid=guid
        self.final=None
        self.exceptionSeen=False
        self.starttime = datetime.now()
        self.startstamp = logging.nowstamp()
        print("MyConversation initialized")
        
    def on_new_code(self,value):
        print("on new code: "+value)        
    
    def on_done(self):
        print("on done")        

    def on_exception(self,value):
        self.exceptionSeen=True
        end_time=datetime.now()
        elapsed_time = (end_time - self.starttime).total_seconds()
        logging.log(
            {'guid': self.guid,
             'title': 'code execution exception',
             'timestamp': logging.nowstamp(),
             'duration': elapsed_time,
             'details': str(value),
             })
        print("on exception: "+value)        
    
    def on_return(self,value):
        if value:
            self.final = str(value)
            print("on return: "+str(value))        
    
    def on_complete(self):
        if self.exceptionSeen:
            return
        end_time=datetime.now()
        elapsed_time = (end_time - self.starttime).total_seconds()
        logging.log(
            {'guid': self.guid,
             'title': 'code execution complete',
             'timestamp': logging.nowstamp(),
             'duration': elapsed_time,
             })
    
    @language_client.managed_function
    def search_email(self, text=None, sender=None, fromWho=None, toRecipients=None, ccRecipients=None, bccRecipients=None, replyTo=None, after=None, before=None, take=None, sort=None, reverse=None):
        try:
            print("search email")
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
                'take': take,
                'sort': sort,
                'reverse': reverse
            }
            print("search email2")

            # Filter out None values
            filtered_params = {k: v for k, v in email_params.items() if v is not None}
            url = "http://127.0.0.1:5001/search_email"
            headers = {
                "Content-Type": "application/json"
            }

            start_time= datetime.now()
            start_stamp=logging.thenstamp(start_time)

            print("search email3")
            response = requests.post(url, headers=headers, data=json.dumps(filtered_params))

            print("search email4")
            end_time=datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            print("search email5")
            result = response.json()
            print("search email6")
            logging.log(
                {'guid': self.guid,
                 'title': 'search_email',
                 'timestamp': start_stamp,
                 'duration': elapsed_time,
                 'parameters': str(filtered_params),
                 'output': result
                 })
            print("search email7")

            self.final=result
            return result
        except Exception as e:
            stack_trace = traceback.format_exc()
            print(f"search email exception {e} -- {stack_trace}")
            end_time=datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            logging.log(
                {'guid': self.guid,
                 'title': 'search_email exception',
                 'timestamp': start_stamp,
                 'duration': elapsed_time,
                 'parameters': str(filtered_params),
                 'exception': f"{e} -- {stack_trace}"
                 })
            print("logged")

     
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
        self.config = {'module_blacklist':['io'], 'exposed_functions':['now']}
        self.client = language_client.ApiConductorClient(self.config, MyConversation)
    
    async def Run(self, code, guid):
        print("creating conversation")
        conversation = MyConversation(self.client, code, guid)
        print("created conversation")
        await conversation.task
        print("finished conversation")
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
