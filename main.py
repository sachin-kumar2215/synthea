# main.py
import asyncio
import logging
import os
import json

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Import the custom orchestrator
from agents.pipeline_agent import root_agent  # DiseaseToSyntheaFlowAgent

# --- Basic config ---
APP_NAME = "disease_profile_app"
USER_ID = "local-user"
SESSION_ID = "cli-session-1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_runner_and_session():
    """
    Create an in-memory session and a Runner for the custom pipeline agent.
    """
    session_service = InMemorySessionService()

    # Initial empty state; you can pre-seed if you want
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={},
    )
    logger.info(f"Created session with initial state: {session.state}")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return session_service, runner


async def chat_loop():
    """
    Very simple REPL-style loop:
      - you type a request (e.g. 'Generate profile + Synthea module for Malaria')
      - the pipeline runs
      - you see only the final text from the last agent (Synthea JSON)
    """
    session_service, runner = await setup_runner_and_session()

    print("Disease Profile + Synthea pipeline (CLI mode). Type 'exit' to quit.\n")

    while True:
        user_input = input("you> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        # Wrap user input as a Content object (as in ADK examples)
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)],
        )

        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
        )

        final_text = None

        async for event in events:
            # You could print streaming content here if you want,
            # but we'll just capture the final response.
            if event.is_final_response() and event.content and event.content.parts:
                # take first text part
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        final_text = part.text
                        break

        if final_text is not None:
            print("\nagent>")
            print(final_text)
            print()

        # Optional: inspect state (for debugging)
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        # Uncomment if you want to see state updates (e.g. disease_profile, synthea_module_json)
        # print("STATE:", json.dumps(session.state, indent=2))


if __name__ == "__main__":
    asyncio.run(chat_loop())
