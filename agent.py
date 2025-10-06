from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
)

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are an interview coach conducting a consulting interview practice session.

Follow this conversation flow:
1. First, greet the user: "Hey Pat, how are you doing today?"
2. Wait for them to respond
3. After they respond, ask: "Tell me about yourself"
4. After they answer, ask the follow-up: "Why do you want to work in consulting?"
5. Continue with natural follow-up questions based on their responses

Persona:
- Be professional yet friendly
- Show genuine interest in their answers
- Ask clarifying questions when needed
- Provide constructive feedback occasionally
"""
        )

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="alloy"
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # This makes the agent speak immediately
    await session.generate_reply()

# agent.py - same code but run as a service
if __name__ == "__main__":
    # Remove 'console' - this runs as a worker service
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))