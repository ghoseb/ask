# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///
import argparse
import json
import os
import sys

import requests
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text

# --- Configuration ---
MODEL = "deepseek/deepseek-chat-v3-0324:free"

API_KEY_ENV_VAR = "OPENROUTER_API_KEY"
API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are a helpful assistant. Please provide concise and accurate answers.
Format your answers clearly. Don't be too chatty. Be stoic and to the point.
Example:

User: What is 2+2
Assistant: 4

User: Who is the President of the USA?
Assistant: Donald J. Trump

User: Give me python code to generate the Nth Fibonacci number.
Assistant: ```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```
"""
# --- End Configuration ---

console = Console()  # Standard output
error_console = Console(stderr=True)  # Error output


def get_status_indicator(status):
    """Return the appropriate status indicator based on current state."""
    if status == "waiting":
        return Text("🔴 ", style="red bold")
    elif status == "streaming":
        return Text("🟠 ", style="yellow bold blink")
    elif status == "complete":
        return Text("🟢 ", style="green bold")
    return Text("")


def ask_llm(api_key: str, system_prompt: str, user_question: str):
    """
    Calls the hardcoded LLM API endpoint with the system prompt and user question,
    using a hardcoded model, then streams the response with status indicators.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "ask.py",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_question},
        ],
        "stream": True,
    }

    # Display the user's question
    console.print(f"User: {user_question}", style="bold")

    # Initialize response text as a plain string to collect markdown
    response_content = ""

    # Start with waiting status
    with Live(
        Text.assemble(get_status_indicator("waiting"), "Assistant: "),
        refresh_per_second=10,
    ) as live:
        try:
            with requests.post(
                API_ENDPOINT, headers=headers, json=payload, stream=True, timeout=180
            ) as response:
                response.raise_for_status()

                # Update to streaming status
                live.update(
                    Text.assemble(get_status_indicator("streaming"), "Assistant: ")
                )

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data:"):
                            json_data_str = decoded_line[len("data:") :].strip()
                            if json_data_str == "[DONE]":
                                break
                            if not json_data_str:
                                continue
                            try:
                                data = json.loads(json_data_str)
                                content = (
                                    data.get("choices", [{}])[0]
                                    .get("delta", {})
                                    .get("content")
                                )
                                if content:
                                    response_content += content
                                    # Show plain text during streaming
                                    display_text = Text.assemble(
                                        get_status_indicator("streaming"),
                                        "Assistant: ",
                                        response_content,
                                    )
                                    live.update(display_text)
                            except (json.JSONDecodeError, IndexError, KeyError) as e:
                                # Print warning but continue processing stream if possible
                                error_console.print(
                                    f"\n[Warning: Stream processing error: {e} on chunk: {json_data_str}]",
                                    style="yellow",
                                )

                # When complete, render markdown
                try:
                    # Create a composite renderable with status indicator and markdown
                    status_text = Text.assemble(
                        get_status_indicator("complete"), "Assistant:"
                    )
                    live.update(status_text)
                    # Stop the live display to render the final markdown
                    live.stop()
                    # Render markdown separately after the status indicator
                    console.print(Markdown(response_content))
                except Exception as e:
                    # Fallback to plain text if markdown rendering fails
                    error_console.print(
                        f"\nMarkdown rendering error: {e}. Displaying as plain text:",
                        style="yellow",
                    )
                    console.print(response_content)

        except requests.exceptions.HTTPError as e:
            error_details = e.response.text
            try:
                error_json = e.response.json()
                error_details = json.dumps(error_json, indent=2)
            except json.JSONDecodeError:
                pass
            error_console.print(
                f"\nAPI HTTP Error ({e.response.status_code}): {e}\nResponse body:\n{error_details}",
                style="red bold",
            )
            sys.exit(1)  # Exit on HTTP error
        except requests.exceptions.RequestException as e:
            error_console.print(f"\nAPI Request Error: {e}", style="red bold")
            sys.exit(1)  # Exit on connection error
        except Exception as e:
            error_console.print(
                f"\nAn unexpected error occurred: {e}", style="red bold"
            )
            sys.exit(1)  # Exit on other unexpected errors


def main():
    """Handle command line arguments and call the LLM API."""
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        error_console.print(
            f"Error: Environment variable {API_KEY_ENV_VAR} is not set.",
            style="red bold",
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description=f"Ask a question to the LLM ({MODEL} model via {API_ENDPOINT}). Requires {API_KEY_ENV_VAR} env var."
    )
    _ = parser.add_argument(
        "question",
        type=str,
        nargs="+",  # Accept multiple words as a single question argument
        help="The question to ask the LLM.",
    )

    args = parser.parse_args()

    user_question = " ".join(args.question)  # Join the words back into a single string

    if not user_question.strip():
        parser.error("The 'question' argument cannot be empty.")

    ask_llm(api_key=api_key, system_prompt=SYSTEM_PROMPT, user_question=user_question)


if __name__ == "__main__":
    main()
