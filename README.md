# AgriSathi

*The farmer's digital companion.*

AgriSathi is a multilingual voice agent that gives Indian farmers agricultural
advice over an ordinary phone call. It is built on LiveKit Agents and uses
Google Gemini as the reasoning model, with Deepgram for speech-to-text and
Cartesia for speech synthesis. The design goal is zero-friction access: no
smartphone, no app, and no internet on the farmer's side, only a voice call.

## Why this exists

India has well over a hundred million farmers, many of whom do not use
smartphones or apps. AgriSathi meets them where they already are, on the
phone, and answers questions about crops, weather, market prices, and
government schemes in the farmer's own language.

## How it works

When a call arrives, LiveKit routes it to a worker. The agent identifies the
caller by phone number, loads any saved profile and recent conversation
history from a local SQLite database, and starts a voice session:

- **Speech-to-text:** Deepgram Nova-3, configured for multilingual input
- **Language model:** Google Gemini, used through the LiveKit Google plugin
- **Text-to-speech:** Cartesia Sonic-3
- **Voice activity detection:** Silero VAD with a multilingual turn detector

The agent greets the farmer, detects their language from the first words, and
mirrors it for the rest of the call. It can register a farmer's details,
remember their preferred language and crops, and run a web search grounded in
Google Search to answer questions about schemes, prices, and weather.

When a call ends, the conversation is summarized and stored so the next call
can continue where the last one stopped. A watchdog ends the call after a
configurable time limit to keep sessions bounded.

## Architecture

| Layer | Technology |
| --- | --- |
| Orchestration | LiveKit Agents |
| Speech-to-text | Deepgram Nova-3 |
| Language model | Google Gemini |
| Text-to-speech | Cartesia Sonic-3 |
| Voice activity detection | Silero + multilingual turn detector |
| Web search | Gemini with Google Search grounding |
| Call summarization | Groq (Llama 3.1 8B) |
| Memory | SQLite |

## Project layout

- `src/agent.py` — call entrypoint, session setup, and the agent definition
- `src/config.py` — environment configuration and startup validation
- `src/database.py` — SQLite storage for farmer profiles and conversation summaries
- `src/prompt.py` — system prompt defining the agent's persona and behavior
- `src/state.py` — per-process session state helpers
- `src/tools/` — functions the agent can call (registration, language, web search)
- `src/handlers/` — conversation tracking and post-call summarization
- `src/utils/telephony.py` — call hang-up helper

## Getting started

Requirements: Python 3.11+ and [uv](https://github.com/astral-sh/uv).

1. Install dependencies:

   ```
   uv sync
   ```

2. Copy `.env.example` to `.env` and fill in your API keys.

3. Run the worker in development mode:

   ```
   python -m src.main dev
   ```

   For production, build and run the included container image, or start the
   worker directly:

   ```
   python -m src.main start
   ```

## Deployment

A `Dockerfile` is included. It installs dependencies from the lockfile and
runs the worker with `uv run src/main.py start`. The `download-files` command
pre-fetches models at build time so the container is ready to run.

## Notes

This project was built as a learning exercise with an emphasis on clear,
modular code. The current memory store is a local SQLite file, which is
appropriate for a single worker. If the worker is scaled horizontally, the
SQLite file would be replaced with a shared database.

## License

MIT
