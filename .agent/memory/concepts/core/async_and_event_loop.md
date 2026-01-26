# Python Asyncio Internals: Coroutines, Event Loop, and Cooperative Multitasking

**Category**: core
**Difficulty**: 6 (Python Internals + Concurrency Model)
**Status**: mastered
**Related**: [websockets, livekit_agent_structure]

## One-Liner
Asyncio implements **cooperative multitasking** using **coroutines** (pausable functions) scheduled by a single-threaded **event loop** that multiplexes I/O operations.

## The Technical Foundation

### What is a Coroutine?

A coroutine is a **generator-based function** that can suspend and resume execution while preserving its state.

```python
async def my_coroutine():
    print("Start")
    await asyncio.sleep(1)  # Suspension point
    print("End")
```

**What happens when you call it**:
```python
coro = my_coroutine()  # Returns a coroutine object, does NOT execute
# coro is now a <coroutine object> with __await__() method
```

**Internally**: `async def` creates a special generator that implements the `__await__()` protocol. When you `await` it, Python calls `__await__()` which yields control.

### The `await` Keyword: What It Actually Does

```python
result = await some_async_function()
```

### Simple Explanation First: The Pizza Delivery Analogy

When you `await something()`, it's like ordering pizza:
1. You call the pizza place (start async function)
2. They give you a receipt saying "30 minutes" (returns a **Future** - a promise of pizza later)
3. You **don't stare at the door** - you go back to work (function pauses, event loop runs other tasks)
4. Doorbell rings (Future completes) - you get your pizza (result arrives)
5. You continue what you were doing (execution resumes after `await`)

### Technical Step-by-Step

```python
result = await some_async_function()
```

**What actually happens**:

**Step 1: Returns a coroutine object**
```python
coro = some_async_function()  # Doesn't run yet! Just creates a "recipe"
```
- Calling an `async def` function returns a **coroutine object** (not the result)
- Think of it as a "pausable recipe" that can be executed later

**Step 2: `await` activates the coroutine**
- `await` calls `coroutine.__await__()` which returns an **iterator**
- This iterator will "yield" control when it needs to wait for something

**Step 3: Yields a Future to the event loop**
- The iterator yields a **Future** object (a "ticket" representing a result that will arrive later)
- **What's a Future?** A placeholder object with two states:
  - `Pending`: "I'm still waiting for the result"
  - `Done`: "I have the result!"

**Step 4: Current coroutine suspends**
- Your function **pauses** and saves its state:
  - Which line it was on
  - All local variables
  - The call stack
- Like pausing a video game and saving your progress

**Step 5: Event loop runs other tasks**
- While you're waiting, the event loop switches to other tasks
- Like doing emails while waiting for pizza delivery
- This is why async is efficient - no idle CPU time

**Step 6: Future completes, coroutine resumes**
- When the result arrives, event loop calls `.send(result)` on the coroutine
- Your function "wakes up" exactly where it paused
- The result is passed back

**Step 7: Execution continues**
- Your code continues after the `await` line with the result available

**Critical**: `await` is syntactic sugar for `yield from` (Python 3.4 style). It's a **controlled yield** to the event loop.

### Complete Working Example

Here's a real example showing all 7 steps:

```python
import asyncio

async def fetch_weather():
    """Simulates fetching weather from an API"""
    print("  [fetch_weather] Starting API call...")
    await asyncio.sleep(2)  # Simulates network delay
    print("  [fetch_weather] Got response!")
    return "Sunny, 25°C"

async def main():
    print("1. Before calling fetch_weather()")
    
    # Step 1: Calling async function returns coroutine (doesn't run yet)
    print("2. Calling fetch_weather() - returns coroutine object")
    
    # Steps 2-7 happen during this await:
    print("3. About to await (function will pause here)...")
    result = await fetch_weather()
    # ^ Your code pauses here while fetch_weather runs
    # Event loop can run other tasks during the sleep(2)
    
    print(f"4. Resumed! Got result: {result}")
    print("5. Continuing with rest of main()")

# Run it
asyncio.run(main())
```

**Output**:
```
1. Before calling fetch_weather()
2. Calling fetch_weather() - returns coroutine object
3. About to await (function will pause here)...
  [fetch_weather] Starting API call...
  [fetch_weather] Got response!
4. Resumed! Got result: Sunny, 25°C
5. Continuing with rest of main()
```

**What happened during the `await`**:
1. `fetch_weather()` started running
2. Hit `await asyncio.sleep(2)` - yielded a Future to event loop
3. `main()` paused (suspended)
4. Event loop waited 2 seconds (could run other tasks here)
5. Sleep completed, event loop resumed `fetch_weather()`
6. `fetch_weather()` returned "Sunny, 25°C"
7. Event loop resumed `main()` with the result

### The Event Loop: The Single-Threaded Scheduler

The event loop is an infinite loop that:
1. Checks which I/O operations are ready (using OS primitives: `epoll` on Linux, `kqueue` on macOS, `IOCP` on Windows)
2. Runs callbacks for completed operations
3. Schedules coroutines to resume
4. Repeats

**Pseudocode**:
```python
while True:
    # Check OS for ready file descriptors
    ready_fds = selector.select(timeout=0)
    
    # Run callbacks for ready operations
    for fd in ready_fds:
        callback = fd_to_callback[fd]
        callback()
    
    # Run all scheduled tasks
    while task_queue:
        task = task_queue.pop()
        task.step()  # Resume coroutine until next await
```

**Key Insight**: Only **one** line of Python bytecode executes at a time (due to the GIL). Asyncio doesn't give you parallelism—it gives you **concurrency** by avoiding idle time during I/O waits.

### Cooperative vs Preemptive Multitasking

| Cooperative (Asyncio) | Preemptive (Threads) |
|-----------------------|----------------------|
| Task **must** yield control (`await`) | OS can interrupt at **any** time |
| No race conditions (single-threaded) | Race conditions possible |
| If task doesn't yield, **entire system freezes** | Other threads keep running |
| Efficient for I/O-bound work | Better for CPU-bound work |

### Visual Timeline: How Event Loop Switches Tasks

Imagine you have 2 farmers calling AgriSathi at the same time:

```
Time →
0ms:  [Farmer 1] Agent starts, await ctx.connect()
      [Event Loop] Switches to Farmer 2
      
10ms: [Farmer 2] Agent starts, await ctx.connect()
      [Event Loop] Both waiting for network, CPU is idle
      
50ms: [Farmer 1] Connection ready! Resume agent
      [Farmer 1] await assistant.say("Namaste")
      [Event Loop] Switches to Farmer 2
      
60ms: [Farmer 2] Connection ready! Resume agent
      [Farmer 2] await assistant.say("Namaste")
      [Event Loop] Both waiting for Gemini response
      
200ms:[Farmer 1] Gemini response ready! Resume agent
      [Farmer 1] Plays audio, await next input
      [Event Loop] Switches to Farmer 2
      
210ms:[Farmer 2] Gemini response ready! Resume agent
      ...and so on
```

**Key insight**: One CPU core handles both farmers because most time is spent **waiting** (network, Gemini), not computing. The event loop ensures the CPU is never idle.

**Danger Zone**:
```python
async def bad_task():
    while True:
        compute_pi()  # CPU-bound, no await
        # This BLOCKS the entire event loop!
```

If you run this, **all other tasks freeze**. The event loop can't run anything else because this task never yields.

### Futures and Tasks

**Future**: A placeholder for a result that will arrive later.
```python
future = asyncio.Future()
# Later...
future.set_result(42)
await future  # Returns 42
```

**Task**: A wrapper that schedules a coroutine on the event loop.
```python
task = asyncio.create_task(my_coroutine())
# my_coroutine() now runs concurrently
await task  # Wait for it to finish
```

**Under the hood**: `create_task()` wraps the coroutine in a `Task` object and adds it to the event loop's run queue.

## In AgriSathi: Handling Multiple Farmers

```python
# src/main.py
async def entrypoint(ctx: JobContext):
    agent = AgriSathiAgent(ctx)
    await agent.start()
```

**When 3 farmers call simultaneously**:
1. LiveKit spawns 3 **Tasks** (one per call), all running in the **same Python process**
2. Each task runs `entrypoint(ctx)` with a different `ctx` (different room)
3. When Farmer 1's agent hits `await assistant.say(...)`, it yields to the event loop
4. Event loop switches to Farmer 2's task, which might be at `await ctx.connect()`
5. While both are waiting (network I/O), event loop handles Farmer 3
6. When Gemini responds to Farmer 1, event loop resumes that task

**Result**: One CPU core handles 3 (or 100) concurrent calls because most time is spent **waiting** for network I/O, not computing.

### The Global Interpreter Lock (GIL)

Python's GIL means only one thread can execute Python bytecode at a time. Asyncio **doesn't bypass the GIL**—it just ensures the single thread is never idle.

**When GIL matters**:
- CPU-bound work (image processing, ML inference): Use `multiprocessing` or offload to C extensions
- I/O-bound work (network, disk): Asyncio is perfect

## Technical Terms for Interviews

| Term | Definition |
|------|------------|
| **Coroutine** | A function that can suspend/resume, implemented as a generator with `__await__()` |
| **Event Loop** | Single-threaded scheduler that multiplexes I/O using OS primitives (epoll/kqueue) |
| **Future** | A placeholder for a result that hasn't arrived yet |
| **Task** | A coroutine wrapped for scheduling on the event loop |
| **Cooperative Multitasking** | Tasks must explicitly yield control (vs preemptive where OS interrupts) |
| **Selector** | OS-level API for monitoring multiple file descriptors (epoll, kqueue, select) |

## Common Mistakes

1. **Forgetting to await**:
   ```python
   my_coroutine()  # Returns coroutine object, doesn't run!
   await my_coroutine()  # Actually runs
   ```

2. **Blocking the event loop**:
   ```python
   time.sleep(1)  # BLOCKS everything
   await asyncio.sleep(1)  # Yields to event loop
   ```

3. **Mixing sync and async**:
   ```python
   def sync_function():
       await something()  # SyntaxError! Can't await in sync function
   ```

## User Notes
- User correctly identified: "We use async when a function is time-consuming and we want it to be stoppable"
- Missing piece: It's not just "stoppable"—it's about **yielding control** so other tasks can run during the wait
- The event loop is the **only** thing that actually runs; coroutines just yield to it
