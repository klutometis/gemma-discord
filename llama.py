import logging

import discord
from absl import app
from langchain_groq import ChatGroq

import bot


def get_llama():
    return ChatGroq(
        temperature=1.0,
        groq_api_key=bot.get_param("groq"),
        model_name="llama3-70b-8192",
    )


def main(argv):
    # Define the intents
    intents = discord.Intents.default()

    # Initialize Client
    client = discord.Client(intents=intents)

    # Event listener for when the client has switched from offline to online
    @client.event
    async def on_ready():
        logging.info(f"Logged in as {client.user}")

    # Event listener for when a message is sent to a channel the client is in
    @client.event
    async def on_message(message):
        # Don't let the client respond to its own messages
        if message.author == client.user:
            return

        # Check if the client was mentioned in the message
        if (
            client.user.mentioned_in(message)
            and message.mention_everyone is False
        ):
            return await bot.prompt(message, get_llama())

    client.run(bot.get_param("groq_token"))


if __name__ == "__main__":
    app.run(main)
