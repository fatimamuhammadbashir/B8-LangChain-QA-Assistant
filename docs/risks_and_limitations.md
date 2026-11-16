# B8 Risks and Limitations

This document describes the practical risks of running the FIP B8 LangChain Q&A assistant and the limits of what the project can prove. The assistant is an educational prototype, not a production service.

---

## 1. API costs and usage

OpenAI API usage is **billed separately from a ChatGPT subscription**. A ChatGPT plan does not automatically provide API credits.

Costs depend on:

- the selected model (`OPENAI_MODEL`, with `gpt-6-luna` as the project default);
- the number of input tokens: system prompt + last three exchanges + current question;
- the number of output tokens;
- retries and repeated requests;
- current OpenAI pricing, which can change.

Practical controls:

- Check the current OpenAI pricing page before running a large number of questions.
- Set a spending limit or budget alert in the OpenAI dashboard.
- Keep the conversation history short; this project caps it at three exchanges.
- Avoid unnecessary retries and repeated identical questions.
- Monitor usage after testing sessions.
- Do not assume a free tier or trial credit is available.

The project makes no cost estimate because prices, model access, and token counts vary by account and request.

---

## 2. API key security

The API key is a secret with billing access. Treat it like a password.

Project safeguards:

- The key is read from `OPENAI_API_KEY` or a local `.env` file.
- `.env` is listed in `.gitignore` and must never be committed.
- `.env.example` contains placeholders only.
- Code reports only whether a key is configured, never the key value.
- `MissingAPIKeyError` stops the program before a client is created.
- Error translation does not include the key, request headers, or raw response bodies.

User responsibilities:

- Never paste a real key into source code, the notebook, tests, README, screenshots, chat messages, or issue trackers.
- Do not share `.env` or copy it to another machine.
- Use a dedicated key with the least access needed for this project.
- Revoke and replace the key immediately if it is exposed.
- Remember that deleting a key from a file does not remove it from shell history, editor backups, or version-control history.
- On a shared computer, protect the project folder and avoid leaving the key in environment variables for other users.

No real API key is included in this project.

---

## 3. Internet dependency

Live answers require:

- a working internet connection;
- access to `api.openai.com`;
- a valid API key;
- access to the selected model;
- available API credits or quota.

If the network is unavailable, the client may raise `APIConnectionError` or `APITimeoutError`. The project translates these into short friendly messages, but it cannot produce a live answer offline.

The offline tests do not require internet access because they use `FakeListChatModel`. That is a test convenience, not an offline version of the assistant.

---

## 4. Model errors and hallucinations

A large language model can produce answers that are:

- factually wrong;
- outdated;
- incomplete;
- confidently phrased but unsupported;
- inconsistent between runs;
- based on a mistaken interpretation of the question.

The system prompt asks the assistant to answer clearly, admit uncertainty, and avoid inventing facts, sources, or citations. A prompt instruction **reduces** some bad behaviour but does **not guarantee** correctness.

This project has:

- no document retrieval;
- no database or knowledge base;
- no verification step;
- no citation checking;
- no evaluation benchmark for answer accuracy.

Users should verify important claims against authoritative sources and should not rely on the assistant for medical, legal, financial, safety, or other high-stakes decisions.

---

## 5. Privacy and data transmission

When a live question is sent, the request includes:

- the system prompt;
- the last three question/answer exchanges;
- the current question.

This content is transmitted over HTTPS to OpenAI's API for processing. OpenAI's handling of API data is governed by its own policies and the account's settings, not by this project.

Risks:

- Questions may contain personal, confidential, or proprietary information.
- Conversation history is resent with later questions, increasing what is transmitted.
- Terminal logs, notebook outputs, screenshots, or saved transcripts may retain questions and answers.
- A shared computer or shared OpenAI account may expose conversation data to others.

Recommendations:

- Do not submit secrets, passwords, personal data, client data, or confidential business information.
- Use fictional or anonymised examples for testing.
- Clear notebook outputs and terminal transcripts before sharing the project.
- Review the OpenAI data policy and your organisation's rules before live use.

The notebook and the five Q&A evidence file in `outputs/` contain no live API data.

---

## 6. Missing API key and authentication errors

These are different failure modes:

### Missing API key

`MissingAPIKeyError` is raised by `create_assistant()` when `OPENAI_API_KEY` is missing or empty.

- It happens **before** `ChatOpenAI` is created.
- No network request is made.
- The interactive program prints a short setup message and exits.
- Fix: create `.env`, set `OPENAI_API_KEY`, and restart the program.

### Authentication error

`AuthenticationError` is an OpenAI API exception returned **after** a request is sent.

- It usually means the key is invalid, revoked, expired, or inactive.
- The project converts it to: "Authentication failed. Check that OPENAI_API_KEY is valid and active, then restart the assistant."
- Fix: check the key in the OpenAI dashboard, replace it, and restart.

Related API errors:

| Error | Meaning | Practical response |
|---|---|---|
| `PermissionDeniedError` | Key cannot use the selected model | Check project/model access or choose another model |
| `RateLimitError` | Rate limit or quota reached | Check billing/usage and retry later |
| `BadRequestError` | Request rejected, often an invalid model name | Set `OPENAI_MODEL` to a valid model or remove the line |
| `APITimeoutError` | Request exceeded the 30-second timeout | Retry or check the connection |
| `APIConnectionError` | API could not be reached | Check internet access and retry |
| `InternalServerError` | OpenAI server-side problem | Retry later |
| `APIStatusError` | Other HTTP error | Inspect the status code and retry if appropriate |

A missing key must never be "fixed" by placing a key directly in source code, the notebook, or a test file.

---

## 7. Limitations of offline testing

The 11 offline tests use LangChain's `FakeListChatModel` and `unittest.mock`. They make no OpenAI API calls and use no real API key.

What the tests verify:

- normal questions are accepted and trimmed;
- `None`, empty, and whitespace-only questions are rejected;
- question/answer pairs are stored in history;
- only the last three exchanges are kept;
- the assistant returns readable text from a fake model;
- earlier history appears in later prompts;
- a missing key raises `MissingAPIKeyError` before `ChatOpenAI` is created.

What the tests do **not** verify:

- the quality, accuracy, or style of real OpenAI answers;
- real authentication, permissions, quota, or billing;
- network latency, timeouts, or API availability;
- model-specific behaviour or model-access restrictions;
- token usage or cost;
- safety of real user data;
- behaviour under concurrent users or production load.

Passing offline tests means the local plumbing behaves as designed. It does **not** prove that a live API call will succeed or that answers will be correct.

The five examples in `outputs/five_qa_evidence.md` are explicitly labelled **offline simulations**. They are not live OpenAI responses and should not be presented as such.

---

## 8. Other project limitations

- Conversation history is in memory only and is lost when the process exits.
- Only the last three exchanges are available; older context is discarded.
- The assistant has no retrieval, tools, agents, or external knowledge source.
- Answers are not streamed.
- There is no user authentication, rate limiting, audit logging, monitoring, or deployment hardening.
- The model name is configurable, but model access depends on the OpenAI account.
- The project does not include a production evaluation set or accuracy benchmark.
- `requirements.txt` is unpinned, so a future install may resolve different package versions.

---

## 9. Mitigation checklist

Before live use:

- [ ] `.env` exists locally and contains a real key.
- [ ] `.env` is ignored by Git and is not in any archive or screenshot.
- [ ] `OPENAI_MODEL` is a valid model, not `your_model_name_here`.
- [ ] API spending limits and usage alerts are configured.
- [ ] Questions contain no confidential or personal data.
- [ ] Notebook outputs are cleared before sharing.
- [ ] The key is rotated if exposure is suspected.
- [ ] Answers are reviewed before being relied on.
- [ ] Simulated evidence is clearly distinguished from live OpenAI output.
