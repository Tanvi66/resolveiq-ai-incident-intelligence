import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from resolveiq_agent.agent import root_agent


APP_NAME = "resolveiq"
USER_ID = "resolveiq-user"


session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def ask_agent(question: str) -> str:

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=question)
        ],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=content,
    ):

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text

    return final_response
