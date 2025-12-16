# LiveKit Voice Agent

A real-time voice interview coach that simulates realistic consulting interviews. Built with [LiveKit](https://livekit.io/) and OpenAI's Realtime API, this agent conducts challenging interview practice sessions with natural voice conversation.

## What It Does

This agent acts as an **experienced ex-consultant interviewer** who conducts structured interview practice with professional pressure and realistic challenges. Unlike typical friendly coaching tools, it maintains high standards, challenges vague answers, shows impatience, and demands clarity—just like a real consulting interviewer.

### Interview Flow

1. **Greeting** - "How are you doing today?"
2. **Warm-up** - "Tell me about yourself" (90 seconds)
3. **Fit Questions** - "Why consulting?" with probing follow-ups
4. **Behavioral Questions** - Leadership, failure, persuasion scenarios
5. **Case Interview** (Optional) - Candidate-led or interviewer-led cases

### Agent Behavior

- **No Praise Mode**: Responds with neutral acknowledgments ("Okay", "Got it") rather than validation
- **Pressure Testing**: Interrupts rambling, challenges vague answers, shows skepticism
- **Realistic Challenges**: Uses phrases like "What's your point?", "Be specific", "Speed up"
- **Time Pressure**: Enforces time limits and shows impatience when appropriate

## Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager
- LiveKit account ([sign up](https://cloud.livekit.io/))
- OpenAI API key

## Quick Start

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure environment** (create `.env.local`):
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
```

3. **Download ML models** (optional, improves startup):
```bash
uv run agent.py download-files
```

4. **Start the agent**:
```bash
uv run agent.py start
```

## Docker Deployment

```bash
# Build
docker build -t livekit-voice-agent .

# Run
docker run --env-file .env.local livekit-voice-agent
```

## Project Structure

```
├── agent.py              # Main agent implementation (~40 lines)
├── instructions.txt      # Agent behavior and interview coaching rules
├── pyproject.toml        # Python dependencies
├── livekit.toml          # LiveKit configuration
├── Dockerfile            # Container deployment
└── .env.local            # Environment credentials (gitignored)
```

## Key Technologies

- **LiveKit Agents SDK** - Real-time voice communication with plugin support for Anthropic, Cartesia, Deepgram, OpenAI, and Silero
- **OpenAI Realtime API** - Natural voice conversation with "alloy" voice model
- **Noise Cancellation** - BVC (Blind Voice Cancellation) for clear audio
- **Python 3.13+** with UV package manager

## Customization

Edit [instructions.txt](instructions.txt) to modify the agent's:
- Interview style and tone
- Question sequence and flow
- Challenge phrases and feedback style
- Time limits and pacing

## License

MIT
