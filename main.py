import functools
import json

import discord
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import GemmaChatVertexAIModelGarden
from pyparsing import Literal, SkipTo, StringEnd


@functools.cache
def get_param(key: str) -> str:
    with open("params.json", "r") as file:
        return json.load(file)[key]


@functools.cache
def get_gemma() -> GemmaChatVertexAIModelGarden:
    return GemmaChatVertexAIModelGarden(
        project=get_param("project"),
        location=get_param("location"),
        endpoint_id=get_param("endpoint"),
        parse_response=True,
        temperature=0,
    )


# TODO(danenberg): Librarify this: comes up all the time; pull-request
# for langchain?
def parse_gemma(ai_message: AIMessage) -> str:
    grammar = Literal("Output:\n") + SkipTo(
        "<end_of_turn>" | StringEnd()
    ).setResultsName("output")

    return grammar.parseString(ai_message.content)["output"]


# Define the intents
intents = discord.Intents.default()


# Initialize Client
client = discord.Client(intents=intents)


# Event listener for when the client has switched from offline to online
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


# Event listener for when a message is sent to a channel the client is in
@client.event
async def on_message(message):
    # Don't let the client respond to its own messages
    if message.author == client.user:
        return

    # Check if the client was mentioned in the message
    if client.user.mentioned_in(message) and message.mention_everyone is False:
        conversation = ChatPromptTemplate.from_messages(
            [
                HumanMessage(
                    "You are a Discord bot; please respond to user queries "
                    "with brevity and wit. Be funny!"
                ),
                AIMessage("Ok!"),
                HumanMessagePromptTemplate.from_template("{prompt}"),
            ]
        )

        chain = (
            {"prompt": RunnablePassthrough()}
            | conversation
            | get_gemma()
            | parse_gemma
        )

        # Send a direct message to the author
        await message.channel.send(
            f"{message.author.mention}, {await chain.ainvoke(message.content)}"
        )


client.run(get_param("token"))
