import logging

import discord
from absl import app
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

import bot


def get_gemini():
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,  # noqa: 501
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,  # noqa: 501
    }

    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=bot.get_param("gemini"),
        temperature=1.0,
    ).bind(safety_settings=safety_settings)


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
            return await bot.prompt(message, get_gemini())

    client.run(bot.get_param("gemini_token"))


if __name__ == "__main__":
    app.run(main)
