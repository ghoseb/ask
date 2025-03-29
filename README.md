# ask

A simple CLI tool to ask questions to an LLM (Large Language Model) via the OpenRouter API with live response streaming.

## Features

- Quick access to AI assistance from your terminal
- Live streaming of responses with status indicators
- Markdown rendering of responses
- Concise, stoic assistant persona for direct answers
- Minimal dependencies

## Installation

### Prerequisites

- Python 3.12 or higher
- OpenRouter API key ([get one here](https://openrouter.ai/))
- `uv` package manager

### Quick Install

```bash
# Clone the repository or download ask.py
git clone https://github.com/ghoseb/ask.git
cd ask

# Give execute perms to ask shell script
chmod +x ask

# Dependencies are automatically managed through the script header
./ask "How many moons does Jupiter have?"
```

You may want to put the `ask` shell script in your executable path.

## Usage

First, set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Then simply run the script with your question:

```bash
ask "What is the capital of France?"
```

## Examples

```bash
# Ask for information
ask "What is quantum computing?"

# Get code samples
ask Write a Python function to reverse a string

# Request explanations
ask Explain the difference between HTTP and HTTPS
```

## Configuration

The script uses the following defaults:

- Model: `deepseek/deepseek-chat-v3-0324:free`
- API Endpoint: OpenRouter API
- System Prompt: Configured for concise, direct responses

To modify these settings, edit the corresponding variables at the top of the script.

## Troubleshooting

- If you see an error about `OPENROUTER_API_KEY`, make sure you have set the environment variable correctly

## License

Public Domain.
