from Orchestrator import logging
import uuid

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


    def process(self) -> str:
        # You can modify this method to process the user_query as needed
        result = f"Processed: {self.user_query}"
        logging.send_log_message({
           'guid': self.guid,
           'title': "complete",
           'timestamp': logging.nowstamp(),
           'duration': 0,
           'response': result,
           })
        
        return result

