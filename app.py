import os
from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-sonnet-4-5"

def print0(message):
    block = message.content[0]
    if block.type != "text":
        raise ValueError(f"Expected text block, got {block.type}")
    print(block.text)

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    block = message.content[0]
    if block.type != "text":
        raise ValueError(f"Expected text block, got {block.type}")
    return block.text

def main():
    # Anthropic Config
    claude_model = os.getenv("CLAUDE_MODEL", "")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")


    assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
    assert anthropic_api_key, (
        "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
    )

    # Start with an empty message list
    messages = []

    # Add the initial user question
    add_user_message(messages, "Define quantum computing in one sentence")

    # Get Claude's response
    answer = chat(messages)
    print(answer)

    # Add Claude's response to the conversation history
    add_assistant_message(messages, answer)

    # Add a follow-up question
    add_user_message(messages, "Write another sentence")

    answer = chat(messages)
    print(answer)

    # Add Claude's response to the conversation history
    add_assistant_message(messages, answer)

    # Add a follow-up question
    add_user_message(messages, "Write a goodbye")

    final_answer = chat(messages)

    print(final_answer)


if __name__ == "__main__":
    main()
