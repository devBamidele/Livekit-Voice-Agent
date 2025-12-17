
from dotenv import load_dotenv
import json
import os

from livekit import agents, api
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import (
    openai,
    noise_cancellation,
)

load_dotenv(".env.local")

# Store case metadata globally to share between function and entrypoint
case_data: dict[str, str | None] = {"question": None, "difficulty": None}


class Assistant(Agent):
    def __init__(self) -> None:
        # Load instructions from external file
        with open("instructions.txt", "r") as f:
            instructions = f.read()

        super().__init__(instructions=instructions)

    @function_tool()
    async def set_case_metadata(
        self,
        question: str,
        difficulty: str
    ):
        """Called when presenting the market sizing case question to set metadata.

        Args:
            question: The complete market sizing question being asked
            difficulty: The difficulty level - must be one of: easy, medium, or hard
        """
        # Store in global dictionary for the entrypoint to access
        case_data["question"] = question
        case_data["difficulty"] = difficulty

        return {
            "status": "success",
            "message": f"Case metadata set: {difficulty} difficulty"
        }

async def entrypoint(ctx: agents.JobContext):
    # Track if metadata has been set
    metadata_set = False

    # Initialize LiveKit API for room metadata updates
    livekit_api = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            voice="alloy"
        )
    )

    @session.on("function_tools_executed")
    def on_function_executed(event):
        """Listen for function calls and set room metadata"""
        nonlocal metadata_set

        async def set_metadata():
            nonlocal metadata_set

            if not metadata_set and case_data["question"] and case_data["difficulty"]:
                # Set room metadata using Room Service API
                metadata = json.dumps({
                    "caseQuestion": case_data["question"],
                    "difficulty": case_data["difficulty"]
                })

                try:
                    await livekit_api.room.update_room_metadata(
                        api.UpdateRoomMetadataRequest(
                            room=ctx.room.name,
                            metadata=metadata
                        )
                    )
                    print(f"[ROOM METADATA SET] Question: {case_data['question']}, Difficulty: {case_data['difficulty']}")
                    metadata_set = True
                except Exception as e:
                    print(f"[ERROR] Failed to set room metadata: {e}")


        # Create async task as required by LiveKit
        import asyncio
        asyncio.create_task(set_metadata())

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
