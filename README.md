# FIP B8 - LangChain Basics: Basic Q&A Assistant

A small, educational question-and-answer assistant built with **LangChain 1.x** and the **OpenAI API**. The project demonstrates a clear prompt template, a reusable LCEL chain, a short in-memory conversation history, input validation, safe API-key handling, and friendly API error messages.

The assistant is deliberately simple. It is a learning project, not a production service.

---

## Status

| Item | Status |
|---|---|
| Source code | Complete |
| Prompt template and chain | Complete |
| Conversation history (last 3 exchanges) | Complete |
| Input validation | Complete |
| API error handling | Complete |
| Offline tests | **11 passed, 0 failed** |
| Notebook | Complete, not executed |
| Offline simulated Q&A evidence | Complete in `outputs/five_qa_evidence.md` |
| Live OpenAI Q&A evidence | **Pending** - requires a local API key and API credits |

The five examples in `outputs/five_qa_evidence.md` were generated with LangChain's `FakeListChatModel`. They are **simulated**, not live OpenAI responses. A live run is still required if the course requires real API-produced answers.

Live OpenAI API testing was not performed because no API credits were available during project preparation.

---

## Overview

The assistant:

1. Reads `OPENAI_API_KEY` and `OPENAI_MODEL` from the environment or a local `.env` file.
2. Validates and trims the user's question.
3. Builds a prompt containing:
   - a system message that sets a clear teaching-assistant style,
   - the last three question/answer exchanges,
   - the current question.
4. Sends the prompt through:

   ```text
   ChatPromptTemplate | ChatOpenAI | StrOutputParser
   ```

5. Returns a plain-text answer and stores the exchange in memory.
6. Converts common OpenAI errors into short, key-safe messages.

If no API key is configured, the assistant stops with `MissingAPIKeyError` **before** creating an OpenAI client or making a request.

---

## Objectives

- Show how a LangChain prompt template separates instructions from user input.
- Explain the role of `ChatOpenAI` and `StrOutputParser`.
- Demonstrate the LCEL chain syntax `prompt | model | parser`.
- Keep only the last three exchanges so prompts stay small.
- Validate empty input before any API call.
- Load secrets from environment variables without exposing them.
- Handle authentication, rate-limit, connection, timeout, and other API errors.
- Verify the logic offline with `FakeListChatModel` and `unittest`.

---

## Features

| Feature | Implementation |
|---|---|
| Prompt template | `ChatPromptTemplate` with a system message, `MessagesPlaceholder("history")`, and `{question}` |
| Chat model | `ChatOpenAI` with an explicit model, 30-second timeout, and 2 retries |
| Output parser | `StrOutputParser` returns a plain Python string |
| Conversation history | In-memory list of `HumanMessage` / `AIMessage`, trimmed to 3 exchanges (6 messages) |
| Input validation | Rejects `None`, empty strings, and whitespace-only questions |
| Missing key guard | Raises `MissingAPIKeyError` before any network request |
| API error handling | Friendly messages for authentication, permission, rate limit, timeout, connection, bad request, server, and other API errors |
| Interactive mode | `python src/qa_assistant.py` with `quit` / `exit` commands |
| Offline tests | 11 tests using `FakeListChatModel` and `unittest.mock` |
| Notebook | 26-cell educational walkthrough, no stored outputs or API keys |
| Evidence | Five clearly labelled offline simulated Q&A examples |

---

## Project structure

```text
B8/
|-- .env.example
|-- .gitignore
|-- README.md
|-- requirements.txt
|-- docs/
|   `-- risks_and_limitations.md
|-- notebooks/
|   `-- B8_LangChain_QA_Assistant.ipynb
|-- outputs/
|   `-- five_qa_evidence.md
|-- src/
|   `-- qa_assistant.py
|-- tests/
|   `-- test_offline.py
`-- .venv/                       (local virtual environment, not published)
```

The `.venv/` folder and a real `.env` file are ignored by `.gitignore`. No Git repository has been initialized in this project.

---

## Requirements

- Windows (the commands below use PowerShell)
- Python **3.13.17** was used to build the project; Python 3.11+ should work
- Internet access for live OpenAI calls
- An OpenAI API key with available API credits

`requirements.txt` currently lists **unpinned** package names:

```text
langchain
langchain-openai
python-dotenv
notebook
ipykernel
```

At build time, pip resolved these versions:

| Package | Installed version |
|---|---:|
| `langchain` | 1.5.0 |
| `langchain-openai` | 1.8.0 |
| `python-dotenv` | 1.2.4 |
| `notebook` | 7.6.5 |
| `ipykernel` | 7.4.0 |
| `langchain-core` | 1.8.1 (transitive) |
| `openai` | 3.51.0 (transitive) |

Unpinned requirements make the project easy to install but not fully reproducible. For a fixed environment, pin the versions actually installed or keep a `pip freeze` snapshot.

---

## Installation and virtual environment

Open PowerShell in the cloned `B8` project folder, or change into it with `cd`:

```powershell
cd path\to\B8
```

The project already contains `.venv`. To recreate it from scratch:

```powershell
python -m venv .venv
```

Use the interpreter inside the environment directly:

```powershell
.\.venv\Scripts\python.exe --version
```

Optional activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

If script execution is blocked by PowerShell policy, keep using the full `.\.venv\Scripts\python.exe` path instead of activation.

---

## Dependency installation

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Verify the key packages:

```powershell
.\.venv\Scripts\python.exe -m pip show langchain langchain-openai python-dotenv notebook ipykernel
```

Do not install project packages globally. Everything should stay inside `.venv`.

---

## Safe API key configuration

1. Copy the placeholder file:

   ```powershell
   copy .env.example .env
   ```

2. Open `.env` in a text editor and replace the placeholder values.

   ```text
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-6-luna
   ```

   Replace `your_api_key_here` with your own key. Never use the placeholder as a real key.

3. Save the file. Do **not** commit `.env`.

Rules:

- Never paste a real key into `README.md`, the notebook, tests, chat messages, screenshots, or logs.
- Never print, log, or store the key in output files.
- The project code reports only whether a key is configured (`yes` / `no`).
- `.env` is listed in `.gitignore`; `.env.example` contains placeholders only.
- A ChatGPT subscription does **not** automatically include OpenAI API credits. API usage is billed separately.
- Revoke and replace a key immediately if it is exposed.

The code loads `.env` with `load_dotenv(override=False)`, so real environment variables take precedence over the file.

---

## Correct OPENAI_MODEL configuration

`OPENAI_MODEL` must be a real model name that your OpenAI account can use, for example:

```text
OPENAI_MODEL=gpt-6-luna
```

Important:

- If you copy `.env.example`, it contains `OPENAI_MODEL=your_model_name_here`.
- You must replace that value or delete the line.
- If the line is missing or empty, `get_settings()` falls back to `DEFAULT_MODEL = "gpt-6-luna"`.
- Leaving the placeholder unchanged sends an invalid model name and produces a `BadRequestError`.

`langchain-openai` still defaults to `gpt-3.5-turbo`, which OpenAI has shut down. The project therefore always passes an explicit model to `ChatOpenAI`.

---

## Run the assistant

From the B8 folder:

```powershell
.\.venv\Scripts\python.exe src\qa_assistant.py
```

Then type a question:

```text
Your question: What is LangChain?
```

Type `quit` or `exit` to stop. Empty input is rejected before any model call.

If no key is configured, the program prints a short explanation and exits without making a request.

### Run the notebook

```powershell
.\.venv\Scripts\python.exe -m notebook notebooks\B8_LangChain_QA_Assistant.ipynb
```

The notebook is an educational walkthrough. Its runnable cells are designed to work offline with `FakeListChatModel`; live-call snippets are illustrative and should only be used after configuring a key.

---

## Run offline tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected result:

```text
Ran 11 tests in ...s

OK
```

Last verified: **16 November 2026** - **11 passed, 0 failed**.

The tests make no OpenAI API calls and use no real API key. They cover:

- validation of normal, `None`, empty, and whitespace-only questions;
- trimming;
- history storage and the last-three-exchanges limit;
- readable answers from `FakeListChatModel`;
- inclusion of previous history in later prompts;
- `MissingAPIKeyError` before `ChatOpenAI` is created.

---

## Security and limitations

### Security

- No API key is stored in the repository.
- No real `.env` file is included; only `.env.example` with placeholders.
- The key is never printed, logged, or written to output files.
- Live questions and the last three exchanges are transmitted to OpenAI's API over HTTPS.
- Do not send confidential, personal, or sensitive information unless your account and data policy allow it.

### Limitations

- Answers can be wrong, incomplete, or outdated. The assistant has no fact-checking or document retrieval.
- Conversation history is lost when the process ends.
- The assistant keeps only three exchanges, so older context is unavailable.
- Live use requires internet access, a valid key, model access, and API credits.
- Offline tests with `FakeListChatModel` verify plumbing and validation, not real model quality, latency, or quota behaviour.
- The project has no authentication, rate limiting, monitoring, persistence, or production deployment controls.
- The five Q&A examples in `outputs/five_qa_evidence.md` are simulated and are not live OpenAI responses.

See [`docs/risks_and_limitations.md`](docs/risks_and_limitations.md) for the full risk discussion.

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `MissingAPIKeyError` or "No OpenAI API key found" | `OPENAI_API_KEY` is unset or empty | Create `.env` and set a valid key |
| `AuthenticationError` | Key is invalid, revoked, or inactive | Check the key in the OpenAI dashboard and replace it |
| `PermissionDeniedError` | Key cannot access the selected model | Choose a model your account can use |
| `RateLimitError` | Quota or rate limit reached | Check billing/usage and retry later |
| `BadRequestError` | Invalid model name, often the placeholder | Set `OPENAI_MODEL` to a valid model or remove the line |
| `APIConnectionError` / `APITimeoutError` | Network or timeout problem | Check the connection and retry |
| `ModuleNotFoundError` | Dependencies are missing | Install `requirements.txt` into `.venv` |

---

## Documentation

- [`docs/risks_and_limitations.md`](docs/risks_and_limitations.md) - costs, privacy, security, model errors, and offline-testing limits
- [`outputs/five_qa_evidence.md`](outputs/five_qa_evidence.md) - five offline simulated Q&A examples
- [`notebooks/B8_LangChain_QA_Assistant.ipynb`](notebooks/B8_LangChain_QA_Assistant.ipynb) - educational walkthrough
- [`src/qa_assistant.py`](src/qa_assistant.py) - assistant implementation
- [`tests/test_offline.py`](tests/test_offline.py) - offline unit tests
