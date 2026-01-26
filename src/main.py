from livekit.agents import cli, WorkerOptions
import logging
from src.agent import entrypoint
from src.config import Config

# Configure basic logging for the application
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    # Validate config before starting
    try:
        Config.validate() # User needs to fill .env first!
        pass
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        exit(1)

    print("🚀 AgriSathi Worker starting...")
    # Start the worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
