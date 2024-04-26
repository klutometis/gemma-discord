import functools
import json

import pyparsing
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory


@functools.cache
def get_param(key: str) -> str:
    with open("params.json", "r") as file:
        return json.load(file)[key]


def purge_mentions(message: str):
    mentions = (
        pyparsing.Suppress("<@")
        + pyparsing.SkipTo(">", include=True).suppress()
    )
    return mentions.transform_string(message)


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


async def prompt(message, model):
    chat = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                "You are a Discord bot; please respond to user "
                "queries with brevity and wit. Be funny!"
            ),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    chain = chat | model | StrOutputParser()

    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    response = await with_message_history.ainvoke(
        {"input": purge_mentions(message.content)},
        config={"configurable": {"session_id": message.author}},
    )

    # Send a direct message to the author
    return await message.channel.send(f"{message.author.mention}, {response}")
