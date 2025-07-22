# Real-Time Chat Server

FastAPI backend for a real-time chat application with WebSocket support.

## Features

- Real-time messaging via WebSockets
- Multiple chat rooms
- User authentication
- In-memory message storage
- REST API endpoints

## Prerequisites

- Python 3.9+
- pip

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lawrik70/real-time-chat-backend.git
   cd real-time-chat-backend
2. Create and activate virtual environment:
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    pip install -r requirements.txt
3. Run server:
   uvicorn main:app --reload
