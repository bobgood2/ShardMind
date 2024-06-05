from Orchestrator import app_logging as logging, prompt_builder
import uuid
from Orchestrator.llm_client import LLMClient
from Orchestrator.prompt_builder import PromptBuilder
from Orchestrator.plan_runner import PlanRunner
from datetime import datetime, timedelta

llmClient = LLMClient()
promptBuilder = PromptBuilder()
planRunner = PlanRunner()

class Request:
    def __init__(self, user_query: str):
        self.user_query = user_query
        self.guid= str(uuid.uuid4())
        logging.send_log_message({
           'guid': self.guid,
           'title': "user query",
           'timestamp': logging.nowstamp(),
           'duration': 0,
           'query': self.user_query,
           })


    async def llmCall(self):
        start_time= datetime.now()
        start_stamp=logging.thenstamp(start_time)
        prompt = promptBuilder.get('reason', {'QUERY':self.user_query, 'HISTORY':''})
        model = 'dev-gpt-4o-2024-05-13-chat-completions'
        request_data = {
          "messages":[
            {"role": "system", "content": prompt},
            {"role": "user", "content": self.user_query}
          ],
          "temperature": 0.7,
          "top_p": 0.95,
          "max_tokens": 800
        }
        rid = str(uuid.uuid4())
        print("LLMSEND")
        response = await llmClient.send_request(model, request_data, rid)
#        {'id': 'chatcmpl-9V7DFJ2NqQyDod9I6KLUHmR8kCBav', 
#        'object': 'chat.completion', 
#        'created': 1717202921, 
#        'model': 'gpt-4o-2024-05-13', 
#        'choices': [
#          {'index': 0, 
#          'message': 
#          {'role': 'assistant', 'content': 'RESPONSE.\n\nHello! How can I assist you with Microsoft 365 today?'}, 
#          'logprobs': None, 'finish_reason': 'stop'}
#        ], 
#        'usage': {'prompt_tokens': 2050, 
#        'completion_tokens': 16, 
#        'total_tokens': 2066}, 
#        'system_fingerprint': 'fp_5f4bad809a'}
        result = response['choices'][0]['message']['content']        
        print("LLMRESPONSE")
        end_time=datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logging.log(
            {'guid': self.guid,
             'title': 'LLM',
             'timestamp': start_stamp,
             'duration': elapsed_time,
             'prompt': prompt,
             'model': response['model'],
             'prompt_tokens' f"{response['usage']['prompt_tokens']}"
             'completion_tokens' f"{response['usage']['completion_tokens']}"
             'output': result
             })
        return result
        
    async def process(self) -> str:

        # You can modify this method to process the user_query as needed
        result = await self.llmCall()
        print("starting plan: "+result)
        program = await planRunner.Run(result, self.guid)
        return program.final

