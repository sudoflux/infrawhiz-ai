# InfraWhiz

<<<<<<< HEAD
InfraWhiz is a lightweight AI-driven tool that lets you monitor and manage your Linux servers using natural language in a web interface.

## Features

- Connect to multiple Linux servers via SSH
- Collect and visualize system health metrics (CPU, RAM, disk, network)
- Natural language interface for server management
- AI-powered command interpretation (using Claude)
=======
AI-driven Linux server management tool with natural language interface.

## Features

- Connect to Linux servers via SSH
- Monitor system health metrics (CPU, memory, disk, network)
- Natural language interface to query server status and execute commands
- AI-powered command interpretation using Claude
>>>>>>> origin/main
- Confirmation system for destructive actions

## Architecture

<<<<<<< HEAD
### Backend

- Flask server with REST API
- WebSocket support for real-time communication
- SSH connections to Linux servers
- SQLite database for server configuration storage
- AI agent for natural language processing

### Frontend

The backend is designed to work with the React frontend (coming soon). For now, you can use the REST API and WebSocket endpoints directly.
=======
- Frontend: React SPA
- Backend: Flask with WebSockets
- AI: Claude for natural language processing
- Server Connections: Paramiko (SSH)
- Database: SQLite
>>>>>>> origin/main

## Setup

### Prerequisites

<<<<<<< HEAD
- Python 3.11+
- Access to Linux servers via SSH
- [Optional] Claude API key for AI-powered features

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/infrawhiz.git
   cd infrawhiz
   ```

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your Claude API key.

4. Run the setup script:
   ```bash
   ./run.sh
   ```

The server will start on http://localhost:5000.

## API Endpoints

- `GET /api/servers` - List all configured servers
- `POST /api/servers` - Add a new server
- `GET /api/servers/{server_id}` - Get server details
- `PUT /api/servers/{server_id}` - Update server configuration
- `DELETE /api/servers/{server_id}` - Remove a server
- `POST /api/servers/{server_id}/command` - Execute a command
- `GET /api/servers/{server_id}/metrics` - Get server metrics
- `GET /api/command/history` - View command execution history
- `POST /api/process` - Process natural language query

## WebSocket Events

- `connect` - Connect to WebSocket server
- `disconnect` - Disconnect from WebSocket server
- `user_message` - Send a natural language message
- `ai_response` - Receive AI agent response
- `execute_action` - Execute command on server
- `action_result` - Receive command execution result
- `get_metrics` - Request server metrics
- `metrics_update` - Receive updated server metrics

## License

MIT 
=======
- Python 3.8+
- Node.js 14+
- Access to Claude API

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/infrawhiz.git
cd infrawhiz

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
```

### Configuration

1. Create a `.env` file in the root directory with your Claude API key:

```
CLAUDE_API_KEY=your_api_key_here
```

2. Configure your server connections in the web interface

### Running locally

```bash
# Start the backend (from root directory with venv activated)
python app.py

# Start the frontend (in a separate terminal)
cd frontend
npm start
```

Visit `http://localhost:3000` to access the application.
>>>>>>> origin/main
