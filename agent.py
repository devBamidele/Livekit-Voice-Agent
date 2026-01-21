from dotenv import load_dotenv
import asyncio
import json
import os
import time

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
    # Track silence and interview phases
    class SilenceTracker:
        def __init__(self):
            self.current_phase: str = "opening"
            self.silence_start_time: float | None = None
            self.silence_task: asyncio.Task | None = None
            self.prompt_given_at_30s: bool = False

    tracker = SilenceTracker()

    # Track session start time for time-based prompts
    session_start_time = time.time()

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

    async def monitor_silence(tracker: SilenceTracker, session):
        """Monitor silence duration and inject prompts based on phase"""
        try:
            # Wait for 30 seconds
            await asyncio.sleep(30)

            # Check if still silent (user didn't speak during sleep)
            if tracker.silence_start_time is None:
                return  # User spoke, timer was cancelled

            # Deliver first prompt based on phase using generate_reply with instructions
            if tracker.current_phase == "framework":
                await session.generate_reply(instructions="Say exactly: 'Walk me through your thinking'")
                print("[SILENCE PROMPT] 30s in framework")
            elif tracker.current_phase == "calculations":
                await session.generate_reply(instructions="Say exactly: 'Walk me through your calculation out loud'")
                print("[SILENCE PROMPT] 30s in calculations")
                tracker.prompt_given_at_30s = True

            # For calculations phase, wait additional 15s for second prompt
            if tracker.current_phase == "calculations" and tracker.prompt_given_at_30s:
                await asyncio.sleep(15)  # Total 45s from start

                if tracker.silence_start_time is None:
                    return  # User spoke between 30s and 45s

                await session.generate_reply(instructions="Say exactly: 'What's your best estimate?'")
                print("[SILENCE PROMPT] 45s in calculations")

        except asyncio.CancelledError:
            print("[SILENCE MONITOR] Task cancelled")
            pass

    async def monitor_time_prompts(session, start_time):
        """Monitor elapsed time and deliver time-based prompts"""
        try:
            # Wait for 2.5 minutes (150 seconds)
            await asyncio.sleep(150)
            elapsed = time.time() - start_time
            await session.generate_reply(instructions="Say exactly: 'We're about halfway through'")
            print(f"[TIME PROMPT] 2.5 minutes - Halfway prompt delivered (actual elapsed: {elapsed:.1f}s)")

            # Wait for another 1.5 minutes to reach 4 minutes total (90 more seconds)
            await asyncio.sleep(90)
            elapsed = time.time() - start_time
            await session.generate_reply(instructions="Say exactly: 'You have about one minute remaining'")
            print(f"[TIME PROMPT] 4 minutes - One minute remaining prompt delivered (actual elapsed: {elapsed:.1f}s)")

            # Wait for another 30 seconds to reach 4.5 minutes total
            await asyncio.sleep(30)
            elapsed = time.time() - start_time
            await session.generate_reply(instructions="Say exactly: 'Please wrap up your answer'")
            print(f"[TIME PROMPT] 4.5 minutes - Wrap up prompt delivered (actual elapsed: {elapsed:.1f}s)")

        except asyncio.CancelledError:
            print("[TIME MONITOR] Task cancelled")
            pass

    @session.on("function_tools_executed")
    def on_function_executed(event):
        """Listen for function calls and set room metadata"""
        nonlocal metadata_set, tracker

        async def set_metadata():
            nonlocal metadata_set, tracker

            if case_data["question"] and case_data["difficulty"]:
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

                    # TRANSITION: opening → framework after question is stated (first time or when changed)
                    if not metadata_set:
                        tracker.current_phase = "framework"
                        print(f"[PHASE TRANSITION] opening → framework")
                        metadata_set = True
                    else:
                        # Question was changed mid-interview
                        print(f"[METADATA UPDATED] Question changed to: {case_data['question']}")
                except Exception as e:
                    print(f"[ERROR] Failed to set room metadata: {e}")


        # Create async task as required by LiveKit
        import asyncio
        asyncio.create_task(set_metadata())

    @session.on("user_state_changed")
    def on_user_state_changed(event):
        """Track user speech state and manage silence timers"""
        nonlocal tracker

        async def handle_state_change():
            nonlocal tracker

            # User stopped speaking → start silence timer
            if event.new_state == "listening" and event.old_state == "speaking":
                tracker.silence_start_time = time.time()
                tracker.prompt_given_at_30s = False

                # Cancel any existing timer
                if tracker.silence_task and not tracker.silence_task.done():
                    tracker.silence_task.cancel()

                # Start new silence monitoring task
                tracker.silence_task = asyncio.create_task(
                    monitor_silence(tracker, session)
                )
                print(f"[SILENCE START] Phase: {tracker.current_phase}")

            # User started speaking → cancel timers
            elif event.new_state == "speaking":
                if tracker.silence_task and not tracker.silence_task.done():
                    tracker.silence_task.cancel()
                    print(f"[SILENCE CANCELLED] User resumed speaking")
                tracker.silence_start_time = None
                tracker.prompt_given_at_30s = False

        asyncio.create_task(handle_state_change())

    @session.on("user_input_transcribed")
    def on_user_transcribed(event):
        """Monitor user speech to detect phase transitions"""
        nonlocal tracker

        if not event.is_final:
            return  # Only process final transcripts

        transcript_lower = event.transcript.lower()

        # Detect framework → calculations transition
        if tracker.current_phase == "framework":
            calculation_keywords = [
                "multiply", "divide", "calculate", "times", "equals",
                "million", "billion", "thousand", "percent"
            ]
            if any(keyword in transcript_lower for keyword in calculation_keywords):
                tracker.current_phase = "calculations"
                print(f"[PHASE TRANSITION] framework → calculations")

        # Detect calculations → wrapping_up transition
        elif tracker.current_phase == "calculations":
            wrap_keywords = [
                "final answer", "in conclusion", "to summarize",
                "my answer is", "estimate is", "result is"
            ]
            if any(keyword in transcript_lower for keyword in wrap_keywords):
                tracker.current_phase = "wrapping_up"
                print(f"[PHASE TRANSITION] calculations → wrapping_up")

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Start time-based prompt monitoring
    time_monitor_task = asyncio.create_task(
        monitor_time_prompts(session, session_start_time)
    )
    print("[TIME MONITOR] Started - will deliver prompts at 2.5, 4, and 4.5 minutes")

    # This makes the agent speak immediately
    await session.generate_reply()

# agent.py - same code but run as a service
if __name__ == "__main__":
    # Remove 'console' - this runs as a worker service
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="interview-agent"  # Required for explicit dispatch
    ))
