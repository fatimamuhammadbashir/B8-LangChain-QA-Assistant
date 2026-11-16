"""Offline unit tests for the FIP B8 LangChain Q&A assistant.

These tests never call the OpenAI API and never read a real API key. They use
LangChain's FakeListChatModel, an in-memory callback handler and unittest.mock
instead of a live OpenAI client.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch
from uuid import UUID

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.callbacks import BaseCallbackHandler  # noqa: E402
from langchain_core.language_models import FakeListChatModel  # noqa: E402
from langchain_core.messages import (  # noqa: E402
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from src.qa_assistant import (  # noqa: E402
    MAX_EXCHANGES,
    MAX_HISTORY_MESSAGES,
    ConversationHistory,
    MissingAPIKeyError,
    QAAssistant,
    create_assistant,
    validate_question,
)


class PromptCaptureHandler(BaseCallbackHandler):
    """Record the chat messages sent to the model, without any network access."""

    def __init__(self) -> None:
        super().__init__()
        self.prompts: list[list[BaseMessage]] = []

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        for batch in messages:
            self.prompts.append(list(batch))


class ValidateQuestionTests(unittest.TestCase):
    """Question validation must happen before any model call."""

    def test_normal_question_is_accepted(self):
        self.assertEqual(
            validate_question("What is LangChain?"),
            "What is LangChain?",
        )

    def test_surrounding_whitespace_is_removed(self):
        self.assertEqual(
            validate_question("  What is a prompt template?  "),
            "What is a prompt template?",
        )

    def test_none_question_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_question(None)

    def test_empty_question_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_question("")

    def test_whitespace_only_question_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_question("   \t\n  ")


class ConversationHistoryTests(unittest.TestCase):
    """The short history must store exchanges and stay trimmed."""

    def test_stores_question_and_answer_pair(self):
        history = ConversationHistory()
        history.add_exchange(
            "What is a chain?",
            "A chain connects several steps into one pipeline.",
        )

        self.assertEqual(len(history), 2)
        messages = history.messages
        self.assertIsInstance(messages[0], HumanMessage)
        self.assertIsInstance(messages[1], AIMessage)
        self.assertEqual(messages[0].content, "What is a chain?")
        self.assertEqual(
            messages[1].content,
            "A chain connects several steps into one pipeline.",
        )

    def test_keeps_only_the_last_three_exchanges(self):
        history = ConversationHistory()
        for number in range(1, 6):
            history.add_exchange(f"Question {number}", f"Answer {number}")

        self.assertEqual(MAX_EXCHANGES, 3)
        self.assertEqual(MAX_HISTORY_MESSAGES, MAX_EXCHANGES * 2)
        self.assertEqual(len(history), MAX_HISTORY_MESSAGES)

        contents = [message.content for message in history.messages]
        self.assertEqual(
            contents,
            [
                "Question 3",
                "Answer 3",
                "Question 4",
                "Answer 4",
                "Question 5",
                "Answer 5",
            ],
        )
        self.assertIsInstance(history.messages[0], HumanMessage)
        self.assertNotIn("Question 2", contents)
        self.assertNotIn("Answer 2", contents)


class QAAssistantTests(unittest.TestCase):
    """The chain must answer, strip output and reuse short history."""

    def test_returns_readable_answer_with_fake_model(self):
        llm = FakeListChatModel(
            responses=["  A chain links a prompt, a model and an output parser.  "]
        )
        assistant = QAAssistant(llm=llm)

        answer = assistant.ask("What does a chain do?")

        self.assertIsInstance(answer, str)
        self.assertEqual(
            answer,
            "A chain links a prompt, a model and an output parser.",
        )
        self.assertEqual(len(assistant.history), 2)
        self.assertEqual(
            assistant.history.messages[0].content,
            "What does a chain do?",
        )
        self.assertEqual(assistant.history.messages[1].content, answer)

    def test_previous_history_is_included_in_later_prompts(self):
        llm = FakeListChatModel(
            responses=[
                "LangChain is a framework for building LLM applications.",
                "A chain connects steps into a single pipeline.",
            ]
        )
        assistant = QAAssistant(llm=llm)
        capture = PromptCaptureHandler()

        # Add the callback to the existing chain; the assistant logic is
        # unchanged and the fake model still makes no network request.
        assistant.chain = assistant.chain.with_config(callbacks=[capture])

        first_answer = assistant.ask("What is LangChain?")
        second_answer = assistant.ask("What is a chain?")

        self.assertEqual(len(capture.prompts), 2)
        first_prompt, second_prompt = capture.prompts

        # First call: system message plus the current question only.
        self.assertEqual(len(first_prompt), 2)
        self.assertIsInstance(first_prompt[0], SystemMessage)
        self.assertEqual(first_prompt[-1].content, "What is LangChain?")

        # Second call: history from the first exchange is inserted before the
        # new question, and the system message is still present.
        self.assertIsInstance(second_prompt[0], SystemMessage)
        second_contents = [message.content for message in second_prompt]
        self.assertIn("What is LangChain?", second_contents)
        self.assertIn(first_answer, second_contents)
        self.assertEqual(second_prompt[-1].content, "What is a chain?")
        self.assertIn(second_answer, assistant.history.messages[-1].content)

    def test_empty_question_does_not_reach_the_model(self):
        llm = FakeListChatModel(responses=["This answer must not be used."])
        assistant = QAAssistant(llm=llm)

        with self.assertRaises(ValueError):
            assistant.ask("   ")

        self.assertEqual(len(assistant.history), 0)


class MissingAPIKeyTests(unittest.TestCase):
    """A missing key must stop the assistant before the client is created."""

    def test_missing_api_key_raises_before_chatopenai_is_created(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)
            with patch("src.qa_assistant.load_dotenv"):
                with patch("src.qa_assistant.ChatOpenAI") as chat_openai:
                    with self.assertRaises(MissingAPIKeyError) as context:
                        create_assistant()

        chat_openai.assert_not_called()
        self.assertIn("No OpenAI API key found", str(context.exception))
        self.assertIn("No API request was made", str(context.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
