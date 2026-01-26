# Production Logging & Named Loggers

**Category**: core
**Difficulty**: 3
**Status**: mastered
**Related**: [logging_basics.md](file:///c:/Users/H.P/Desktop/Project%20AgriSathi/.agent/memory/concepts/core/logging_basics.md)

## One-Liner
In production, we use `basicConfig` (or a config file) for global settings and `logging.getLogger(__name__)` in every file for granular control and traceability.

## Full Explanation

### Why not just basicConfig?
In a small script, `logging.info()` is fine. But in a project with 50 files:
1. **Traceability**: If you see "Starting process..." in the logs, you don't know which file it came from.
2. **Granularity**: You might want to see `DEBUG` logs from your database module but only `ERROR` logs from the external API library. You can't do this with just the root logger.

### The Production Standard: Named Loggers
In every Python file (`src/agent.py`, `src/config.py`, etc.), we define a local logger:
```python
import logging
logger = logging.getLogger(__name__)

def my_function():
    logger.info("Function started")
```
- `__name__` automatically becomes the path to the file (e.g., `src.agent`).
- The log output will now look like: `2026-01-25 INFO [src.agent] Function started`.

### Combined Approach
1. **App Entry Point (`main.py`)**: Use `logging.basicConfig` to set the global "Master" level and format.
2. **Everywhere else**: Use `logger = logging.getLogger(__name__)`.

## Example (Production Pattern)
**main.py**:
```python
logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s] %(message)s")
```

**agent.py**:
```python
logger = logging.getLogger(__name__)
logger.info("Agent is warming up")
# Output: INFO [src.agent] Agent is warming up
```

## User Notes
- User was curious if we use one or the other. Conclusion: We use both together.
