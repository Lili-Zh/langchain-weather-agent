# Weather Agent with LangChain and Qwen

A simple AI weather agent built with Python, LangChain, and a Qwen model through an OpenAI-compatible API.

This project demonstrates how an LLM can use external tools and how a basic tool-calling agent can evolve from a manually implemented ReAct-style loop into a multi-turn conversational agent with message history.

The repository contains two versions:

- **Weather01.py** — manually implements the tool-calling / ReAct-style loop
- **Weather02.py** — uses LangChain's `create_agent` and supports multi-turn conversations with message history

## Features

- Uses LangChain and `ChatOpenAI`
- Connects to Qwen through an OpenAI-compatible API
- Defines tools with LangChain's `@tool`
- Retrieves real-time weather information from `wttr.in`
- Demonstrates LLM tool calling
- Includes both manual and framework-managed agent implementations
- Supports multi-turn conversations in V2
- Maintains conversation history in V2
- Uses environment variables to keep API credentials out of source code

## Project Structure

```text
langchain-weather-agent/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── Weather01.py
└── Weather02.py
```

## V1 — Manual ReAct-Style Loop

`Weather01.py` demonstrates the basic mechanics behind LLM tool calling by manually implementing the agent loop.

The workflow is:

```text
User
  ↓
LLM
  ↓
Tool Call Decision
  ↓
get_weather()
  ↓
Weather Data
  ↓
LLM
  ↓
Final Answer
```

The program repeatedly:

1. Sends the conversation messages to the LLM.
2. Checks whether the LLM requested a tool call.
3. Executes the requested tool.
4. Adds the tool result back to the message history.
5. Sends the updated messages to the LLM again.
6. Returns the final response when no additional tool call is required.

A simplified version of the loop looks like this:

```python
for step in range(5):
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if not response.tool_calls:
        return response.content

    for tc in response.tool_calls:
        tool_result = tool_map[tc["name"]].invoke(tc["args"])

        messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tc["id"]
            )
        )
```

This version is useful for understanding what happens internally when an LLM uses tools.

## V2 — Multi-Turn Conversational Agent

`Weather02.py` builds on V1 and uses LangChain's `create_agent` abstraction instead of manually managing the tool-calling loop.

```python
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=...
)
```

The main improvement is support for multi-turn conversations.

A `WeatherChat` class maintains the conversation history:

```python
class WeatherChat:

    def __init__(self):
        self.messages = []

    def send(self, user_input: str) -> str:
        self.messages.append(
            HumanMessage(content=user_input)
        )

        result = agent.invoke({
            "messages": self.messages
        })

        self.messages = result["messages"]

        return self.messages[-1].content
```

This allows the agent to use previous messages as context when processing follow-up questions.

For example:

```text
You: How is the weather in Beijing?

Assistant:
Beijing is sunny and 21°C...

You: What about Changsha?

Assistant:
Changsha is currently...

You: Which one is colder?

Assistant:
Changsha is colder based on the weather information above.
```

The third question does not explicitly mention Beijing or Changsha. The agent can interpret it using the conversation history.

### Clearing Conversation History

V2 also supports:

```text
clear
```

which resets the stored message history and starts a new conversation.

Use:

```text
quit
```

or:

```text
exit
```

to close the application.

## V1 vs V2

| Feature | Weather01.py | Weather02.py |
|---|---|---|
| Weather tool | Yes | Yes |
| LangChain `@tool` | Yes | Yes |
| Qwen / OpenAI-compatible API | Yes | Yes |
| Tool calling | Yes | Yes |
| Manual tool-call loop | Yes | No |
| LangChain `create_agent` | No | Yes |
| Multi-turn conversation | No | Yes |
| Conversation history | Per request | Maintained across turns |
| Interactive CLI | No | Yes |
| Clear conversation command | No | Yes |

The two versions are intentionally kept in the repository to show the progression from understanding the low-level mechanics of tool calling to using a higher-level agent abstraction.

## Weather Tool

Both versions use the same `get_weather` tool.

```python
@tool
def get_weather(city: str) -> str:
    ...
```

The tool retrieves current weather information from `wttr.in`, including:

- Weather conditions
- Temperature
- Feels-like temperature
- Humidity
- Wind speed

The LLM does not retrieve the weather itself. Instead, it decides when the weather tool should be called and uses the returned information to generate the final response.

## Installation

Clone the repository:

```bash
git clone https://github.com/Lili-Zh/langchain-weather-agent.git
cd langchain-weather-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

You can copy `.env.example` and provide your own configuration:

```text
DATA_BASE_URL=https://your-api-endpoint.example.com/v1
DATA_MODEL=your-model-name
DATA_API_KEY=your-api-key
```

For example, the project can be configured to use a Qwen model through an OpenAI-compatible API.

The application reads these values with:

```python
model=os.getenv("DATA_MODEL")
api_key=os.getenv("DATA_API_KEY")
base_url=os.getenv("DATA_BASE_URL")
```

> Never commit your real API key or `.env` file to GitHub.

The `.env` file is excluded through `.gitignore`.

## Running V1

Run:

```bash
python Weather01.py
```

The example program asks predefined weather questions and prints the tool-calling process.

Example:

```text
You: 北京今天天气怎么样？

[Step 1] Call tool: get_weather
[Step 1] Tool result: ...

Assistant: ...
```

## Running V2

Run:

```bash
python Weather02.py
```

You can then have an interactive conversation:

```text
==================================================
  天气助手 V2（多轮对话版）
命令：quit 退出 | clear 清空对话
==================================================

你：北京现在天气怎么样？

助手：...

你：那长沙呢？

助手：...

你：哪个更冷？

助手：...
```

Commands:

```text
clear    Clear the conversation history
quit     Exit the application
exit     Exit the application
q        Exit the application
```

## Architecture

### Weather01.py

```text
User Question
      ↓
ChatOpenAI + bound tools
      ↓
Manual ReAct-style loop
      ↓
Tool call?
   ↙       ↘
 Yes        No
  ↓          ↓
get_weather  Final Answer
  ↓
ToolMessage
  ↓
Back to LLM
```

### Weather02.py

```text
User Input
    ↓
WeatherChat
    ↓
Conversation History
    ↓
LangChain create_agent
    ↓
LLM ↔ get_weather
    ↓
Updated Message History
    ↓
Final Answer
```

## What This Project Demonstrates

This project is intentionally small and focuses on several core concepts in agent development:

**Tool Calling**

The LLM can decide when an external function is required and provide structured arguments for that function.

**Agent Loop**

V1 demonstrates how the model, tool call, tool result, and final response form an iterative execution loop.

**Agent Abstraction**

V2 shows how LangChain's `create_agent` can manage the underlying agent execution process.

**Conversation History**

V2 maintains previous messages so that follow-up questions can be interpreted in the context of earlier turns.

**Separation of Reasoning and External Data**

The LLM generates and interprets language, while real weather information comes from an external weather service.

## Security

API credentials are stored locally in `.env`.

The following files and directories are excluded from Git:

```text
.env
.venv/
venv/
__pycache__/
.idea/
```

`.env.example` documents the required configuration without exposing real credentials.

Never hard-code API keys directly in Python source files.

## Technologies

- Python
- LangChain
- LangChain OpenAI
- Qwen
- OpenAI-compatible API
- wttr.in
- Requests
- python-dotenv

## Possible Next Steps

Future versions could extend the project with:

- Additional tools
- Weather forecasts
- Multiple agent tools
- Persistent conversation memory
- LangGraph-based workflows
- Structured outputs
- A web interface
- Streaming responses

## License

This project is intended for learning and demonstration purposes.


