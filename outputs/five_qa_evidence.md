# FIP B8 - Five Q&A Evidence (Offline Simulation)

> **STATUS: OFFLINE SIMULATION - NOT LIVE OPENAI RESPONSES.**
>
> All five answers below were produced with LangChain's `FakeListChatModel` and the project's `QAAssistant` chain. No OpenAI API call was made, no API key was used, and no live model generated these answers. They are illustrative examples only.

---

## Simulation method

- **Model:** `FakeListChatModel` with five pre-written response strings.
- **Chain:** the same project chain, `build_prompt() | FakeListChatModel | StrOutputParser`, accessed through `QAAssistant.ask()`.
- **History:** the assistant kept the last three exchanges (maximum six messages).
- **Network:** none.
- **API key:** none.
- **Run date:** 16 November 2026.

The canned responses were supplied by the project author to demonstrate prompt construction, answer formatting, and history trimming. They are not evidence of OpenAI model quality or accuracy.

---

## Summary

| # | Question | Messages in history after the answer |
|---|---|---:|
| 1 | What is LangChain? | 2 |
| 2 | What is a prompt template, and why use one? | 4 |
| 3 | What does ChatOpenAI do? | 6 |
| 4 | What does StrOutputParser do? | 6 |
| 5 | Why keep only the last three exchanges? | 6 |

After the third exchange, the history remains at six messages because older turns are dropped.

---

## 1. What is LangChain?

**Mode:** Offline simulation (`FakeListChatModel`)

**Question:** What is LangChain?

**Simulated answer:**

> LangChain is a framework for building applications around large language models. It provides reusable prompts, model wrappers, output parsers, and a way to connect those steps into chains.

---

## 2. What is a prompt template, and why use one?

**Mode:** Offline simulation (`FakeListChatModel`)

**Question:** What is a prompt template, and why use one?

**Simulated answer:**

> A prompt template stores reusable instructions and named variables. It keeps the system message and question format consistent and makes prompts easier to test and change.

---

## 3. What does ChatOpenAI do?

**Mode:** Offline simulation (`FakeListChatModel`)

**Question:** What does ChatOpenAI do?

**Simulated answer:**

> ChatOpenAI adapts OpenAI's chat models to LangChain's chat-model interface so the model can be used as one step in a chain. The project sets the model explicitly and reads the key from the environment.

---

## 4. What does StrOutputParser do?

**Mode:** Offline simulation (`FakeListChatModel`)

**Question:** What does StrOutputParser do?

**Simulated answer:**

> StrOutputParser extracts the text from the model's AIMessage and returns a plain Python string, which is easier to print, save, or compare.

---

## 5. Why keep only the last three exchanges?

**Mode:** Offline simulation (`FakeListChatModel`)

**Question:** Why keep only the last three exchanges?

**Simulated answer:**

> Recent turns provide useful context while limiting prompt size, token cost, and the risk of hitting the context limit. Older turns are dropped first.

---

## What this evidence demonstrates

- The prompt template accepts a history list and a question.
- `QAAssistant` returns plain text through `StrOutputParser`.
- History grows by two messages per exchange until the three-exchange limit.
- After the limit is reached, older messages are trimmed.
- The notebook and assistant can be exercised without an API key.

## What this evidence does not demonstrate

- Real OpenAI answer quality, accuracy, or style.
- Successful authentication, model access, quota, or billing.
- Network latency, timeouts, or API availability.
- Token usage or cost.
- Safety or privacy behaviour of a real live request.

These examples must not be presented as live OpenAI responses. A genuine live run remains pending until a valid API key and API credits are available.
