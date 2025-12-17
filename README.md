# LiveKit Voice Agent

A real-time market sizing case interview practice agent. Built with [LiveKit](https://livekit.io/) and OpenAI's Realtime API, this agent simulates a McKinsey interviewer conducting realistic market sizing cases with professional pressure and strategic probing.

## What It Does

This agent acts as an **experienced McKinsey interviewer** who conducts market sizing case interviews. It delivers case questions (easy, medium, or hard), evaluates candidate responses through strategic probing, and maintains professional interview standards with realistic time pressure.

### Interview Flow

1. **Opening (30 seconds)** - Agent presents a randomly selected market sizing question
2. **Framework Identification (1-2 minutes)** - Listens for candidate's approach and probes if unclear
3. **Calculation Phase** - Monitors progress, prompts if silent, challenges assumptions
4. **Sanity Check** - Asks candidate to validate their final answer
5. **Session End** - 5-minute automatic timeout

The agent automatically sets room metadata (case question and difficulty) when presenting the question, enabling external systems to track interview progress.

### Market Sizing Questions

**Easy:** Smartphones sold in US annually, gas stations in LA, pizzas consumed in NYC

**Medium:** Starbucks revenue in Chicago, diapers used in US daily, EV charging station market in CA

**Hard:** Global meal kit subscription market, autonomous taxi revenue in SF by 2030, AI engineer demand by 2028

### Agent Behavior

- **Neutral Tone**: No praise or validation—uses brief acknowledgments ("Okay", "Got it")
- **Strategic Probing**: Asks "Why is that reasonable?" for weak assumptions, "What's your point?" for rambling
- **Information Withholding**: Only clarifies scope/geography when explicitly asked
- **Time Pressure**: Prompts "Speed up" or "You have one minute remaining" based on conversation flow
- **Silent Prevention**: Intervenes if candidate is silent for 30-45 seconds during calculations

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
├── agent.py              # Main agent with set_case_metadata function tool
├── instructions.txt      # Market sizing interview protocol and questions
├── pyproject.toml        # Python dependencies
├── livekit.toml          # LiveKit configuration
├── Dockerfile            # Container deployment
└── .env.local            # Environment credentials (gitignored)
```

## Key Features

- **Function Calling**: Uses OpenAI's function calling to capture case metadata (question + difficulty) and set it as LiveKit room metadata
- **Real-time Voice**: Natural conversation flow with OpenAI Realtime API using "alloy" voice
- **Noise Cancellation**: BVC (Blind Voice Cancellation) for clear audio quality
- **Automatic Metadata**: Sets room metadata when case question is presented, enabling external tracking systems

## Customization

Edit [instructions.txt](instructions.txt) to modify:
- Market sizing questions (add your own easy/medium/hard questions)
- Interview flow and timing cues
- Probing phrases and pressure tactics
- Behavioral guidelines (neutrality, interruption timing, etc.)

## License

MIT
