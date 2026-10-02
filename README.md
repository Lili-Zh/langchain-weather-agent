# Weather Agent with LangChain and Qwen

A simple AI weather assistant built with Python, LangChain, and a Qwen model through an OpenAI-compatible API.

This project demonstrates how an LLM can use tools through a manually implemented ReAct-style loop. When a user asks about the weather, the model decides whether to call the weather tool, receives the tool result, and then generates a natural-language response.

## Features

- Uses LangChain `ChatOpenAI`
- Connects to Qwen through an OpenAI-compatible API
- Implements tool calling with LangChain's `@tool`
- Retrieves weather information from wttr.in
- Implements a simple ReAct-style agent loop manually
- Supports multiple tool-call iterations
- Uses environment variables for API credentials

## How It Works

The basic workflow is:

User Question  
→ LLM  
→ Tool Call Decision  
→ Weather Tool  
→ Weather Data  
→ LLM  
→ Final Answer

For example:


```text
User: How is the weather in Beijing today?

LLM:
Calls get_weather(city="Beijing")

Weather Tool:
Returns current weather information

LLM:
Generates the final response based on the weather data
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/langchain-weather-agent.git
cd langchain-weather-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

You can copy `.env.example` and provide your own configuration:

```env
DATA_BASE_URL=https://your-api-endpoint.example.com/v1
DATA_MODEL=your-model-name
DATA_API_KEY=your-api-key
```

Do not commit your real `.env` file or API keys to GitHub.

## Run

Run the application with:

```bash
python Weather01.py
```

The example program asks questions such as:

```text
北京今天天气怎么样？
长沙现在热不热？
```

The agent determines that weather information is required, calls the `get_weather` tool, and uses the returned data to generate its response.

## ReAct Loop

Instead of relying on a prebuilt agent executor, this project manually implements a simple ReAct-style loop.

The agent repeatedly:

1. Sends the conversation to the LLM.
2. Checks whether the LLM requested a tool call.
3. Executes the requested tool.
4. Adds the tool result back to the conversation.
5. Sends the updated conversation to the LLM.
6. Returns the final response when no additional tool call is required.

This makes the basic mechanics of LLM tool calling easier to understand.

## Security

API credentials are stored in a local `.env` file.

The `.env` file is excluded through `.gitignore` and should never be committed to the repository.

Use `.env.example` to document the required environment variables without exposing real credentials.

## Technologies

- Python
- LangChain
- Qwen
- OpenAI-compatible API
- wttr.in
- python-dotenv
- Requests


