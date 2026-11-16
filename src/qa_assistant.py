"""Basic LangChain Q&A assistant for the FIP B8 project.

This module connects a LangChain prompt template to the OpenAI chat API and
returns plain-text answers. It keeps a short in-memory conversation history,
rejects empty questions, and turns common API failures into friendly messages.

The OpenAI API key is read from the OPENAI_API_KEY environment variable (or a
local .env file) and is never printed or logged. If no key is configured, the
assistant stops before making any network request.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)

DEFAULT_MODEL = "gpt-6-luna"
MAX_EXCHANGES = 3
MAX_HISTORY_MESSAGES = MAX_EXCHANGES * 2
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 2

SYSTEM_PROMPT = (
    "You are a friendly teaching assistant for a beginner programming course. "
    "Answer questions clearly and accurately in plain English, using short "
    "paragraphs or simple bullet points. Avoid unnecessary jargon, and briefly "
    "explain any technical term you must use. If you do not know an answer or "
    "are unsure, say so plainly instead of guessing. Never invent facts, "
    "sources, or citations. Keep each answer focused on the user's question."
)


def load_environment() -> None:
    """Load variables from a local .env file if one exists.

    ``override=False`` keeps real environment variables authoritative and the
    call is safe when no .env file is present. No secret values are printed or
    logged anywhere in this module.
    """
    load_dotenv(override=False)


def get_settings() -> tuple[str | None, str]:
    """Read the API key and model name from the environment.

    The API key is returned only for the future LangChain client. It must never
    be printed, logged, or written to disk.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
    return api_key, model


def validate_question(question: str | None) -> str:
    """Return a trimmed question, or raise ValueError if it is empty."""
    if question is None:
        raise ValueError("Please enter a question.")

    cleaned = question.strip()
    if not cleaned:
        raise ValueError("Please enter a non-empty question.")

    return cleaned


class AssistantError(RuntimeError):
    """Base error whose message is safe to show to the user."""


class MissingAPIKeyError(AssistantError):
    """Raised when OPENAI_API_KEY is not configured."""


@dataclass
class ConversationHistory:
    """Short in-memory conversation history.

    Only the most recent exchanges are kept so prompts stay small and cheap.
    The history lives for the current Python process only and is never saved
    to disk.
    """

    max_messages: int = MAX_HISTORY_MESSAGES
    _messages: list[BaseMessage] = field(default_factory=list, repr=False)

    @property
    def messages(self) -> list[BaseMessage]:
        """Return a copy of the stored messages for the prompt."""
        return list(self._messages)

    def add_exchange(self, question: str, answer: str) -> None:
        """Store one question/answer pair and trim to the configured limit."""
        self._messages.append(HumanMessage(content=question))
        self._messages.append(AIMessage(content=answer))

        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages :]
            # Keep the oldest remaining turn complete: never start with an
            # assistant message that has lost its question.
            if self._messages and not isinstance(self._messages[0], HumanMessage):
                self._messages.pop(0)

    def clear(self) -> None:
        """Remove every stored message."""
        self._messages.clear()

    def __len__(self) -> int:
        """Return the number of stored messages, not exchanges."""
        return len(self._messages)


def build_prompt() -> ChatPromptTemplate:
    """Build the prompt template used for every question.

    The template has three parts:
    * a system message that sets the assistant's behaviour;
    * a placeholder where the short conversation history is inserted;
    * a human message containing the current question.
    """
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )


class QAAssistant:
    """A small question-answering chain with validation and short history."""

    def __init__(
        self,
        llm: BaseChatModel,
        history: ConversationHistory | None = None,
    ) -> None:
        self.llm = llm
        self.history = history if history is not None else ConversationHistory()
        self.prompt = build_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()

    def ask(self, question: str | None) -> str:
        """Validate a question, get an answer, and remember the exchange."""
        cleaned = validate_question(question)

        try:
            answer = self.chain.invoke(
                {"history": self.history.messages, "question": cleaned}
            )
        except OpenAIError as error:
            raise translate_api_error(error) from error

        answer = (answer or "").strip()
        if not answer:
            raise AssistantError(
                "The assistant returned an empty answer. Please try rephrasing "
                "your question."
            )

        self.history.add_exchange(cleaned, answer)
        return answer

    def reset_history(self) -> None:
        """Forget the current conversation."""
        self.history.clear()


def translate_api_error(error: OpenAIError) -> AssistantError:
    """Map an OpenAI exception to a friendly error that never leaks the key."""
    if isinstance(error, APITimeoutError):
        return AssistantError(
            "The request timed out. Check your connection and try again."
        )
    if isinstance(error, APIConnectionError):
        return AssistantError(
            "Could not reach the OpenAI API. Check your internet connection "
            "and try again."
        )
    if isinstance(error, AuthenticationError):
        return AssistantError(
            "Authentication failed. Check that OPENAI_API_KEY is valid and "
            "active, then restart the assistant."
        )
    if isinstance(error, PermissionDeniedError):
        return AssistantError(
            "This API key is not allowed to use the selected model. Check your "
            "OpenAI project access or choose another model."
        )
    if isinstance(error, RateLimitError):
        return AssistantError(
            "The rate limit or API quota was reached. Wait a moment, check "
            "your OpenAI billing and usage, then try again."
        )
    if isinstance(error, BadRequestError):
        return AssistantError(
            "The API rejected the request. Check that OPENAI_MODEL names a "
            "model your account can use."
        )
    if isinstance(error, InternalServerError):
        return AssistantError(
            "OpenAI reported a server error. Please try again shortly."
        )
    if isinstance(error, APIStatusError):
        return AssistantError(
            f"The OpenAI API returned an error (HTTP {error.status_code}). "
            "Please try again."
        )
    return AssistantError(
        f"Unexpected API error ({type(error).__name__}). Please try again."
    )


def create_assistant(
    model: str | None = None,
    api_key: str | None = None,
) -> QAAssistant:
    """Create an assistant from environment settings.

    Raises MissingAPIKeyError before building the client when no key is set,
    so no API request can be made without credentials.
    """
    load_environment()
    env_key, env_model = get_settings()

    key = api_key or env_key
    model_name = model or env_model

    if not key:
        raise MissingAPIKeyError(
            "No OpenAI API key found. Set OPENAI_API_KEY in your environment "
            "or in a local .env file (see .env.example). No API request was "
            "made."
        )

    llm = ChatOpenAI(
        model=model_name,
        api_key=key,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=MAX_RETRIES,
    )
    return QAAssistant(llm=llm)


def main() -> None:
    """Run a simple interactive question-and-answer session."""
    load_environment()
    api_key, model = get_settings()

    if not api_key:
        print("No OpenAI API key found.")
        print("Set OPENAI_API_KEY in your environment or in a local .env file.")
        print("Copy .env.example to .env and add your own key.")
        print("No API request was made.")
        return

    try:
        assistant = create_assistant()
    except MissingAPIKeyError as error:
        print(error)
        return

    print("FIP B8 - Basic LangChain Q&A Assistant")
    print(f"Model: {model}")
    print("Type 'quit' or 'exit' to stop.")
    print(f"Only the last {MAX_EXCHANGES} exchanges are kept in memory.")
    print("Answers come from an AI model and may contain mistakes.")

    while True:
        try:
            question = input("\nYour question: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.strip().lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        if not question.strip():
            print("Please enter a non-empty question.")
            continue

        try:
            answer = assistant.ask(question)
        except ValueError as error:
            print(f"Input error: {error}")
        except AssistantError as error:
            print(f"Error: {error}")
        else:
            print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
