import sys
import os
import chainlit as cl
from Orchestrator import logging
from Orchestrator import user_request

# Start debugpy and wait for the debugger to attach
print(f"Process ID: {os.getpid()}")
# print("Waiting for debugger attach...")
# debugpy.listen(("localhost", 5678))
# debugpy.wait_for_client()
# print("Debugger attached")
# print(f"Running Python version: {sys.version}")

cl.Message

@cl.on_message
async def on_message(chainlit_message):
    try:
        message = chainlit_message.content
        print("MESSAGE")
        print(str(message))
        request = user_request.Request(message)
        response = request.process()
        await cl.Message(content=response).send()
    except Exception as e:
        print(f"Error in on_message: {e}")

if __name__ == "__main__":
    cl.run()
