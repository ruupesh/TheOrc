# Browser Automation Agent

A specialized browser automation agent that navigates web pages, takes screenshots, fills forms, extracts content, and performs web testing.

## MCP Server

Uses `@modelcontextprotocol/server-puppeteer` (npx) — the official Puppeteer MCP server.

### Tools Provided
- `puppeteer_navigate` — Navigate to a URL
- `puppeteer_screenshot` — Take a screenshot of the current page or element
- `puppeteer_click` — Click an element on the page
- `puppeteer_fill` — Fill in an input field
- `puppeteer_select` — Select an option from a dropdown
- `puppeteer_hover` — Hover over an element
- `puppeteer_evaluate` — Execute JavaScript in the browser

## Prerequisites

- **Chrome/Chromium** must be installed on the system.
- Node.js 18+ for npx.

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. Ensure Chrome/Chromium is installed and accessible.
3. No additional authentication required.

## Running

```bash
uvicorn app.agentic.browser_automation.agent:a2a_app --host 0.0.0.0 --port 8008
```

## Port: 8008
