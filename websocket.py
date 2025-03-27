import logging
from typing import Dict, Any, List, Optional
from flask_socketio import SocketIO
import db
from ssh_manager import ssh_manager
from ai_agent import ai_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SocketIO instance
socketio = SocketIO()

def init_socketio(app):
    """Initialize SocketIO with the Flask app."""
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")
    register_handlers()
    logger.info("SocketIO initialized with eventlet async mode")

def register_handlers():
    """Register SocketIO event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        logger.info("Client connected")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info("Client disconnected")
    
    @socketio.on('user_message')
    def handle_message(data):
        """Process user message and return AI response."""
        user_input = data.get('message', '')
        logger.info(f"Received message: {user_input}")
        
        # Process the user input through the AI agent
        response = ai_agent.process_input(user_input)
        
        # Send response back to the client
        socketio.emit('ai_response', {
            'message': response['message'],
            'actions': response.get('actions', [])
        })
    
    @socketio.on('execute_action')
    def handle_execute_action(data):
        """Execute a command on a server."""
        action_type = data.get('action')
        server_id = data.get('server_id')
        command = data.get('command')
        
        logger.info(f"Executing action: {action_type} on server {server_id}, command: {command}")
        
        if not server_id or not command:
            socketio.emit('action_result', {
                'success': False,
                'error': 'Invalid request: Missing server_id or command',
                'action': action_type
            })
            return
        
        # Get server details
        server = db.get_server(server_id)
        if not server:
            socketio.emit('action_result', {
                'success': False,
                'error': f'Server with ID {server_id} not found',
                'action': action_type
            })
            return
        
        # Ensure we have a connection to the server
        if not ssh_manager.get_connection(server_id):
            # Try to establish connection
            connection_result = ssh_manager.connect(
                server_id=server_id,
                hostname=server['hostname'],
                username=server['username'],
                password=server.get('password'),
                key_path=server.get('key_path'),
                port=server.get('port', 22)
            )
            
            if not connection_result:
                socketio.emit('action_result', {
                    'success': False,
                    'error': f'Failed to connect to server {server["name"]}',
                    'action': action_type
                })
                return
        
        # Execute the command
        result = ssh_manager.execute_command(server_id, command)
        
        # Log the command to history
        db.add_command_history(
            server_id=server_id,
            command=command,
            output=result.get('stdout', '') + '\n' + result.get('stderr', ''),
            exit_code=result.get('exit_code')
        )
        
        # Send result back to client
        socketio.emit('action_result', {
            'action': action_type,
            'server_id': server_id,
            'result': result
        })
    
    @socketio.on('get_metrics')
    def handle_get_metrics(data):
        """Get system metrics from a server."""
        server_id = data.get('server_id')
        
        if not server_id:
            socketio.emit('metrics_update', {
                'success': False,
                'error': 'Invalid request: Missing server_id'
            })
            return
        
        # Get server details
        server = db.get_server(server_id)
        if not server:
            socketio.emit('metrics_update', {
                'success': False,
                'error': f'Server with ID {server_id} not found'
            })
            return
        
        # Ensure we have a connection to the server
        if not ssh_manager.get_connection(server_id):
            # Try to establish connection
            connection_result = ssh_manager.connect(
                server_id=server_id,
                hostname=server['hostname'],
                username=server['username'],
                password=server.get('password'),
                key_path=server.get('key_path'),
                port=server.get('port', 22)
            )
            
            if not connection_result:
                socketio.emit('metrics_update', {
                    'success': False,
                    'error': f'Failed to connect to server {server["name"]}'
                })
                return
        
        # Get metrics
        metrics = ssh_manager.get_server_metrics(server_id)
        
        # Send metrics back to client
        socketio.emit('metrics_update', {
            'server_id': server_id,
            'metrics': metrics
        })
        
        # If successful, also send a formatted message
        if metrics.get('success', False):
            formatted_metrics = ai_agent.format_metrics(metrics)
            socketio.emit('ai_response', {
                'message': formatted_metrics,
                'actions': []
            })

def emit_to_clients(event: str, data: Dict[str, Any]):
    """Utility function to emit events to all connected clients."""
    socketio.emit(event, data) 