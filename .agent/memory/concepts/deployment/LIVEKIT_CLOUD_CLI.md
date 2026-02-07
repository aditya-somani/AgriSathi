# LiveKit CLI (lk) reference

## 🚀 Deployment & Config
| Command | What it does |
| :--- | :--- |
| **`lk agent deploy`** | Re-builds and deploys your code. Run this after ANY code or secret change. |
| **`lk agent create`** | Initial setup to register agent and generate Dockerfile. |
| **`lk agent list`** | Lists your deployed agents and their IDs. |
| **`lk secret list`** | Shows which environment variables are set (values are hidden). |
| **`lk secret set KEY=VALUE`** | updates or adds a new environment variable. |

## 🔍 Monitoring & Debugging
| Command | What it does |
| :--- | :--- |
| **`lk agent logs`** | Streams live logs from your active agent instances. |
| **`lk agent status`** | Shows if your agent is sending/receiving, connected, or restarting. |
| **`lk room list`** | See active rooms (current calls). Useful to check if a call is actually active. |
| **`lk room delete <room_name>`** | Forcefully kill a stuck room/call. |

## 🛠️ Testing
| Command | What it does |
| :--- | :--- |
| **`lk token create --join`** | Generates a quick token you can use in the [Sample App](https://agents-playground.livekit.io/) to test manually. |

## 🔧 Fixes Used in Session
- **Docker Import Error**: Added `ENV PYTHONPATH=/app` to Dockerfile.
- **Config Validation**: Moved `Config.validate()` to `prewarm_fnc` to avoid build-time errors when secrets aren't present.
