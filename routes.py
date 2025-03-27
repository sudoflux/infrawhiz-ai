import logging
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, List, Optional
import db
from ssh_manager import ssh_manager
from ai_agent import ai_agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/servers', methods=['GET'])
def get_servers():
    """Get all configured servers."""
    try:
        servers = db.get_servers()
        return jsonify(servers)
    except Exception as e:
        logger.error(f"Error retrieving servers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>', methods=['GET'])
def get_server(server_id):
    """Get a specific server by ID."""
    try:
        server = db.get_server(server_id)
        if server:
            # Don't expose password in response
            if 'password' in server:
                del server['password']
            return jsonify(server)
        return jsonify({'error': 'Server not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers', methods=['POST'])
def add_server():
    """Add a new server."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'hostname', 'username']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if at least one auth method is provided
        if not data.get('password') and not data.get('key_path'):
            return jsonify({'error': 'Either password or key_path must be provided'}), 400
        
        # Add the server
        server = db.add_server(
            name=data['name'],
            hostname=data['hostname'],
            username=data['username'],
            password=data.get('password'),
            key_path=data.get('key_path'),
            port=data.get('port', 22)
        )
        
        return jsonify(server), 201
    except Exception as e:
        logger.error(f"Error adding server: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>', methods=['PUT'])
def update_server(server_id):
    """Update server details."""
    try:
        data = request.json
        
        # Get the existing server
        server = db.get_server(server_id)
        if not server:
            return jsonify({'error': 'Server not found'}), 404
        
        # Update the server
        success = db.update_server(server_id, **data)
        
        if success:
            # Get the updated server
            updated_server = db.get_server(server_id)
            # Don't expose password in response
            if 'password' in updated_server:
                del updated_server['password']
            return jsonify(updated_server)
        
        return jsonify({'error': 'Failed to update server'}), 500
    except Exception as e:
        logger.error(f"Error updating server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>', methods=['DELETE'])
def delete_server(server_id):
    """Delete a server."""
    try:
        # Disconnect if connected
        ssh_manager.disconnect(server_id)
        
        # Delete from database
        success = db.delete_server(server_id)
        
        if success:
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'Server not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>/connect', methods=['POST'])
def connect_server(server_id):
    """Connect to a server."""
    try:
        # Get the server
        server = db.get_server(server_id)
        if not server:
            return jsonify({'error': 'Server not found'}), 404
        
        # Connect to the server
        success = ssh_manager.connect(
            server_id=server_id,
            hostname=server['hostname'],
            username=server['username'],
            password=server.get('password'),
            key_path=server.get('key_path'),
            port=server.get('port', 22)
        )
        
        if success:
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'Failed to connect to server'}), 500
    except Exception as e:
        logger.error(f"Error connecting to server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>/disconnect', methods=['POST'])
def disconnect_server(server_id):
    """Disconnect from a server."""
    try:
        success = ssh_manager.disconnect(server_id)
        
        if success:
            return jsonify({'success': True}), 200
        
        return jsonify({'error': 'Server not connected or not found'}), 404
    except Exception as e:
        logger.error(f"Error disconnecting from server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>/command', methods=['POST'])
def execute_command(server_id):
    """Execute a command on a server."""
    try:
        data = request.json
        
        if 'command' not in data:
            return jsonify({'error': 'Missing required field: command'}), 400
        
        command = data['command']
        
        # Get the server
        server = db.get_server(server_id)
        if not server:
            return jsonify({'error': 'Server not found'}), 404
        
        # Ensure connected
        if not ssh_manager.get_connection(server_id):
            # Try to connect
            success = ssh_manager.connect(
                server_id=server_id,
                hostname=server['hostname'],
                username=server['username'],
                password=server.get('password'),
                key_path=server.get('key_path'),
                port=server.get('port', 22)
            )
            
            if not success:
                return jsonify({'error': 'Failed to connect to server'}), 500
        
        # Execute the command
        result = ssh_manager.execute_command(server_id, command)
        
        # Log the command to history
        db.add_command_history(
            server_id=server_id,
            command=command,
            output=result.get('stdout', '') + '\n' + result.get('stderr', ''),
            exit_code=result.get('exit_code')
        )
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error executing command on server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/servers/<server_id>/metrics', methods=['GET'])
def get_server_metrics(server_id):
    """Get metrics from a server."""
    try:
        # Get the server
        server = db.get_server(server_id)
        if not server:
            return jsonify({'error': 'Server not found'}), 404
        
        # Ensure connected
        if not ssh_manager.get_connection(server_id):
            # Try to connect
            success = ssh_manager.connect(
                server_id=server_id,
                hostname=server['hostname'],
                username=server['username'],
                password=server.get('password'),
                key_path=server.get('key_path'),
                port=server.get('port', 22)
            )
            
            if not success:
                return jsonify({'error': 'Failed to connect to server'}), 500
        
        # Get metrics
        metrics = ssh_manager.get_server_metrics(server_id)
        
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f"Error getting metrics from server {server_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/command/history', methods=['GET'])
def get_command_history():
    """Get command execution history."""
    try:
        server_id = request.args.get('server_id')
        limit = request.args.get('limit', 50, type=int)
        
        history = db.get_command_history(server_id, limit)
        
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"Error retrieving command history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/process', methods=['POST'])
def process_query():
    """Process a natural language query."""
    try:
        data = request.json
        
        if 'query' not in data:
            return jsonify({'error': 'Missing required field: query'}), 400
        
        query = data['query']
        
        # Process the query through the AI agent
        response = ai_agent.process_input(query)
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500 