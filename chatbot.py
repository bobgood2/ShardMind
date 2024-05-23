import chainlit as cl

@cl.on_message
async def on_message(message: str):
    response = f"Hello, you said: {message}"
    await cl.send_message(response)
