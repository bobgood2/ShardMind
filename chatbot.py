import sys
import os
import debugpy
import chainlit as cl

# Start debugpy and wait for the debugger to attach
print(f"Process ID: {os.getpid()}")
# print("Waiting for debugger attach...")
# debugpy.listen(("localhost", 5678))
# debugpy.wait_for_client()
# print("Debugger attached")
# print(f"Running Python version: {sys.version}")

@cl.on_message
async def on_message(message: str):
    try:
        response = f"Hello, you said: {message.content}"
        await cl.Message(content=response).send()
    except Exception as e:
        print(f"Error in on_message: {e}")

if __name__ == "__main__":
    cl.run()
