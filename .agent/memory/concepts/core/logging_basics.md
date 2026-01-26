# Python Logging Basics

**Category**: core
**Difficulty**: 2
**Status**: mastered
**Related**: [main.py](file:///c:/Users/H.P/Desktop/Project%20AgriSathi/src/main.py)

## One-Liner
`logging.basicConfig` is a quick way to configure the "Root Logger" to output messages to the console or a file at a specific importance level.

## Full Explanation

### The Root Logger vs. Custom Loggers
In Python, there is always a "Root" logger which is the parent of all other loggers.
- `logging.basicConfig(...)` configures this **Root** logger.
- `logging.getLogger(__name__)` creates a **specific** logger for a module.

### Why use basicConfig?
Without configuration, the root logger won't output anything below `WARNING` level. `basicConfig` allows you to set the level (e.g., `INFO`, `DEBUG`) and the format of the messages globally for the entire application.

### Key Components
1. **Level**: What's the minimum importance? (`DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`)
2. **Handlers**: Where do the logs go? (Console, File, Network)
3. **Formatters**: How do the logs look? (Timestamp, name of file, message)

## Example
```python
import logging

# Set up the global configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# This will now appear in the console
logging.info("This is an info message")
```

## User Notes
- Confused about the difference between a `logger` object and `basicConfig`.
- Common point of confusion: `basicConfig` only works once (the first time it's called).
