# LiveKit Voice Agent

A real-time voice interview coach agent built with [LiveKit](https://livekit.io/) and OpenAI's Realtime API. This agent conducts interactive consulting interview practice sessions with natural voice conversation.

## Features

- **Real-time Voice Interaction**: Uses OpenAI's Realtime API for natural voice conversations
- **Interview Coaching**: Conducts structured consulting interview practice sessions
- **Noise Cancellation**: Built-in background noise cancellation for clear audio
- **Docker Support**: Containerized deployment ready

## Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager
- LiveKit account and credentials
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/devBamidele/livekit-voice-agent.git
cd livekit-voice-agent
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Create a `.env.local` file with your credentials:
```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Running Locally

Download required ML models first:
```bash
uv run agent.py download-files
```

Start the agent:
```bash
uv run agent.py start
```

### Running with Docker

Build the Docker image:
```bash
docker build -t livekit-voice-agent .
```

Run the container:
```bash
docker run --env-file .env.local livekit-voice-agent
```

## How It Works

The agent follows a structured interview flow:

1. Greets the participant
2. Asks "Tell me about yourself"
3. Follows up with "Why do you want to work in consulting?"
4. Continues with natural follow-up questions based on responses

The agent maintains a professional yet friendly persona, showing genuine interest and providing constructive feedback.

## Project Structure

- `agent.py` - Main agent implementation
- `Dockerfile` - Container configuration
- `pyproject.toml` - Python dependencies
- `livekit.toml` - LiveKit configuration
- `.env.local` - Environment variables (not tracked in git)

## Dependencies

- `livekit-agents` - LiveKit Agents SDK with multiple plugin support
- `livekit-plugins-noise-cancellation` - Background noise cancellation
- `python-dotenv` - Environment variable management

## License

MIT
