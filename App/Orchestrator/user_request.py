from Orchestrator import app_logging as logging, prompt_builder
import uuid
import traceback
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


    async def llmCall(self, promptName, history):
        start_time= datetime.now()
        start_stamp=logging.thenstamp(start_time)
        prompt = promptBuilder.get(promptName, {'QUERY':self.user_query, 'HISTORY':history})
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
        response = await llmClient.send_request(model, request_data, rid)
        result = response['choices'][0]['message']['content']        
        end_time=datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logging.log(
            {'guid': self.guid,
             'title': 'LLM',
             'timestamp': start_stamp,
             'duration': elapsed_time,
             'promptName': promptName,
             'prompt': prompt,
             'model': response['model'],
             'prompt_tokens': f"{response['usage']['prompt_tokens']}",
             'completion_tokens': f"{response['usage']['completion_tokens']}",
             'output': result
             })
        return result
        
    async def process(self) -> str:
        try:
            history=[]
            promptName='reason'
            iteration=0
            while iteration<3:
                iteration+=1
                # You can modify this method to process the user_query as needed
                result = await self.llmCall(promptName, str(history))
                print("starting plan: "+result)
                if result.startswith("RESPONSE"):
                    print("RESPONSE")
                    text = '\n'.join(result.split('\n')[1:])
                    return text
                if promptName=='synthesis':
                    return result;
                program = await planRunner.Run(result, self.guid)
                history.append({'plan':str(result), 'result':program.final})
                promptName='synthesis'
            return program.final
        except Exception as e:
            stack_trace = traceback.format_exc()
            print(f"Exception {str(e)}")
            print(stack_trace)
            logging.log(
                {'guid': self.guid,
                 'title': 'exception',
                 'message': str(e),
                 'stack trace': stack_trace
                 })
            

