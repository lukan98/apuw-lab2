# XHR Chat (APUW Lab 2)

A small browser-based chat application that demonstrates three client–server communication techniques:

- **Polling** — the client periodically asks the server for new messages
- **Long polling** — the server keeps the request open until a message arrives or a timeout expires
- **WebSockets** — a persistent bidirectional connection

The project was written for the **Architecture, Protocols and Web Services (APUW)** course at FER, University of Zagreb.

## Requirements

- Python 3.11.9 (pinned in `.tool-versions`; the code requires 3.8 or newer)
- The `websockets` Python package

Install the pinned Python version and dependencies:

```bash
asdf install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

From this directory:

```bash
python3 server.py
```

The server starts:

- an HTTP server on **http://localhost:8008**
- a WebSocket server on **ws://localhost:8080**

Open `http://localhost:8008` in **two browser windows or tabs**:

1. In the first window, enter a nickname (for example `alice`) and set "Chat with" to `bob`.
2. In the second window, enter `bob` and set "Chat with" to `alice`.
3. Choose a communication mode and start sending messages.

## Project structure

```text
server.py             # HTTP + WebSocket server and message routing
frontend/
├── html/index.html   # chat UI
├── css/style.css
└── js/script.js      # polling, long-polling and WebSocket client logic
```

## Notes

- Messages are kept in memory only; there is no database or authentication.
- The HTTP and WebSocket servers run in separate threads from the same process.
