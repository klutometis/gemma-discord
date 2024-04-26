import asyncio
import functools
import json
import logging

import discord
import pyparsing
from absl import app
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq


@functools.cache
def get_param(key: str) -> str:
    with open("params.json", "r") as file:
        return json.load(file)[key]


def get_llama():
    return ChatGroq(
        temperature=1.0,
        groq_api_key=get_param("groq"),
        model_name="llama3-70b-8192",
    )


def purge_mentions(message: str):
    mentions = (
        pyparsing.Suppress("<@")
        + pyparsing.SkipTo(">", include=True).suppress()
    )
    return mentions.transform_string(message)


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

        purged_content = purge_mentions(message.content)

        # Check if the client was mentioned in the message
        if (
            client.user.mentioned_in(message)
            and message.mention_everyone is False
        ):
            logging.info(purged_content)

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        "You are a Discord bot; please respond to user queries with brevity and wit. Be funny!"
                    ),
                    AIMessage("Ok!"),
                    HumanMessagePromptTemplate.from_template("{prompt}"),
                ]
            )

            chain = (
                {"prompt": RunnablePassthrough()}
                | prompt
                | get_llama()
                | StrOutputParser()
            )

            # Send a direct message to the author
            await message.channel.send(
                f"{message.author.mention}, {await chain.ainvoke(purged_content)}"
            )

    client.run(get_param("groq_token"))


if __name__ == "__main__":
    app.run(main)
