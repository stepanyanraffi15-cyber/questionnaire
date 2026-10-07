# 028 · One model provider on the author's own Gemini key, plain functions, no orchestration framework

- Status: accepted
- Requirements: the assignment brief's "Include a working programmatic model integration and saved responses from real
  calls using your simulated inputs. Use model access agreed with the hiring team; no particular provider or latest
  model is required." and "Model frameworks, cloud deployment, authentication, fine-tuning, streaming, and multiple
  collaborating agents are optional." Ambiguity AMB-12 (model access).

## Context

The brief asks for "model access agreed with the hiring team", and its notes to the hiring team say "Provide model
access with a spending cap or agree an equivalent before the assignment starts." No access was requested from, or
agreed with, the hiring team.

The pipeline per question is short and linear: build a prompt, call the model, parse, run the mechanical checks, call
the model again for a support check, decide a status in code. The placeholder dependencies in `pyproject.toml` came
from planning and include LangGraph and LangChain packages. Those wrappers need a key when they are constructed and do
not hand back the raw provider response, which complicates saving and replaying real responses.

## Options considered

Model access:
1. **Ask the hiring team for access first.** The author chose not to.
2. **The author's own Google Gemini API key.**
3. **The author's own Anthropic API key.** Kept only as a contingency.

Shape:
1. **One provider (Google Gemini via `google-genai`), plain Python functions, two prompts (draft, support check).**
2. **Two providers (one drafts, another judges).** A cross-family judge reduces self-preference, but doubles adapters
   and settings to explain.
3. **LangGraph orchestration.** No branching or loops that need a graph.

## Decision

Model access option 2 and shape option 1. The app uses the author's own Gemini API key. No access was requested from
the hiring team, and the README says exactly that and never claims an agreement. Default model `gemini-3.8-flash`,
re-checked against the official model list before any recording; thinking level set explicitly; temperature, top-p and
top-k not set; retries through the SDK's options; settings in `config/models.toml`. LangGraph and LangChain are not
used. If Anthropic access is ever used instead, one adapter is built behind the same seam. A cross-family judge is
optional work.

## Consequences

- Dependencies: `google-genai`, `pydantic`, `streamlit`, `python-dotenv`; dev `pytest`, `ruff`. The LangGraph and
  LangChain packages are removed and `uv.lock` updated.
- Limitation: the support check and the grader's judge (decision 027) belong to the same model family as the drafter,
  so self-preference is possible; stated in the README.
- Live calls happen only in an explicit recording run; replay needs no key (decision 029).

## Evidence

- `pyproject.toml` (placeholder dependencies).
- `uv.lock` (pins `google-genai`).
