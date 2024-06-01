import sys
import os
import chainlit as cl
from Orchestrator import logging
from Orchestrator import user_request

print(f"Process ID: {os.getpid()}")

cl.Message

@cl.on_message
async def on_message(chainlit_message):
    try:
        message = chainlit_message.content
        print("MESSAGE")
        print(str(message))
        request = user_request.Request(message)
        print("PROCESS")
        response = await request.process()
        print("SEND")
        await cl.Message(content=response).send()
    except Exception as e:
        print(f"Error in on_message: {e}")

if __name__ == "__main__":
    cl.run()
