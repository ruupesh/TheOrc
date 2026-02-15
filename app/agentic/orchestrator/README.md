# Supervisor (Orchestrator Agent)

The Supervisor is the central intelligence of the multi-agent system. It acts as a project manager that decomposes complex user requests into structured execution plans, delegates tasks to specialized sub-agents, and utilizes internal tools to deliver finalized solutions.

## Features

- **Task Decomposition**: Breaks down high-level user prompts into atomic, logical steps.
- **Agent Delegation**: Automatically hands off specialized tasks to sub-agents like the `job_search_assistant`.
- **Tool Integration**: Uses built-in tools for calculations, weather checks, and file path resolution.
- **Synthesis**: Combines outputs from multiple sources into a coherent final response.

## Prerequisites

Ensure you have the following environment variables set in your `.env` file:

- `AGENT_MODEL`: The LLM model to use (e.g., `gemini/gemini-1.5-pro` or `gpt-4o`).

## Sub-Agents

- **Job Search Assistant**: A remote agent (running on port 8001) that finds job opportunities and saves them to disk.

## Tools

- `check_prime`: Checks if a list of numbers are prime.
- `check_weather`: Retrieves real-time weather data for a given location.
- `find_file_path`: Resolves local file paths.

## How to Run

The Orchestrator is typically run using the ADK Web interface for interactive testing.

1. Ensure the sub-agents (e.g., `job_search_assistant`) are already running.
2. From the project root directory, run:
   ```powershell
   adk web src/agents
   ```

This will launch a web interface where you can interact with the Supervisor agent and observe how it orchestrates tasks across tools and sub-agents.

