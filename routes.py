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
    """
    Legacy endpoint for processing natural language queries.
    """
    try:
        data = request.json
        
        if 'input' not in data:
            return jsonify({'error': 'Missing required field: input'}), 400
        
        user_input = data['input']
        
        # Process the input
        result = ai_agent.process_input(user_input)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/query', methods=['POST'])
def natural_language_query():
    """
    Process a natural language query and perform the requested action.
    
    Accepts a JSON payload with 'input' field containing the natural language query.
    Returns the results of executing the parsed intent.
    """
    try:
        data = request.json
        
        if 'input' not in data:
            return jsonify({'error': 'Missing required field: input'}), 400
        
        user_input = data['input']
        logger.info(f"Processing natural language query: {user_input}")
        
        # Parse the natural language input
        parsed_intent = ai_agent.parse_user_input(user_input)
        logger.info(f"Parsed intent: {parsed_intent}")
        
        # Extract intent information
        intent = parsed_intent.get('intent')
        target_server = parsed_intent.get('target_server')
        action = parsed_intent.get('action')
        
        # Validate parsed data
        if not intent or not action:
            return jsonify({
                'success': False,
                'message': 'Could not understand the query.',
                'parsed_intent': parsed_intent
            }), 400
        
        # Get server ID from name if not "all"
        servers_to_process = []
        if target_server == "all":
            servers = db.get_servers()
            if not servers:
                return jsonify({
                    'success': False,
                    'message': 'No servers are configured.',
                    'parsed_intent': parsed_intent
                }), 404
            servers_to_process = servers
        else:
            # Find the server by name
            all_servers = db.get_servers()
            matching_servers = [s for s in all_servers if s['name'].lower() == target_server.lower()]
            
            if not matching_servers:
                return jsonify({
                    'success': False,
                    'message': f'Server "{target_server}" not found.',
                    'parsed_intent': parsed_intent
                }), 404
            
            servers_to_process = matching_servers
        
        # Process based on intent
        results = []
        
        for server in servers_to_process:
            server_id = server['id']
            server_name = server['name']
            
            # Ensure connection is established
            if not ssh_manager.get_connection(server_id):
                connection_result = ssh_manager.connect(
                    server_id=server_id,
                    hostname=server['hostname'],
                    username=server['username'],
                    password=server.get('password'),
                    key_path=server.get('key_path'),
                    port=server.get('port', 22)
                )
                
                if not connection_result:
                    results.append({
                        'server': server_name,
                        'success': False,
                        'message': f'Failed to connect to server {server_name}'
                    })
                    continue
            
            if intent == 'metrics':
                # Get metrics from server
                if action == 'cpu':
                    metrics = ssh_manager.get_server_metrics(server_id)
                    if metrics['success']:
                        results.append({
                            'server': server_name,
                            'success': True,
                            'message': f"CPU usage on {server_name}: {metrics.get('cpu_usage', 'Unknown')}%",
                            'data': {
                                'cpu_usage': metrics.get('cpu_usage')
                            }
                        })
                    else:
                        results.append({
                            'server': server_name,
                            'success': False,
                            'message': f"Failed to get CPU metrics from {server_name}",
                            'error': metrics.get('error', 'Unknown error')
                        })
                
                elif action == 'memory':
                    metrics = ssh_manager.get_server_metrics(server_id)
                    if metrics['success']:
                        results.append({
                            'server': server_name,
                            'success': True,
                            'message': (
                                f"Memory usage on {server_name}: {metrics.get('memory_percent', 'Unknown')}% "
                                f"({metrics.get('memory_used', 'Unknown')}MB / {metrics.get('memory_total', 'Unknown')}MB)"
                            ),
                            'data': {
                                'memory_percent': metrics.get('memory_percent'),
                                'memory_used': metrics.get('memory_used'),
                                'memory_total': metrics.get('memory_total')
                            }
                        })
                    else:
                        results.append({
                            'server': server_name,
                            'success': False,
                            'message': f"Failed to get memory metrics from {server_name}",
                            'error': metrics.get('error', 'Unknown error')
                        })
                
                elif action == 'disk':
                    metrics = ssh_manager.get_server_metrics(server_id)
                    if metrics['success']:
                        results.append({
                            'server': server_name,
                            'success': True,
                            'message': f"Disk usage on {server_name}: {metrics.get('disk_percent', 'Unknown')}%",
                            'data': {
                                'disk_percent': metrics.get('disk_percent')
                            }
                        })
                    else:
                        results.append({
                            'server': server_name,
                            'success': False,
                            'message': f"Failed to get disk metrics from {server_name}",
                            'error': metrics.get('error', 'Unknown error')
                        })
                
                else:  # general metrics
                    metrics = ssh_manager.get_server_metrics(server_id)
                    if metrics['success']:
                        results.append({
                            'server': server_name,
                            'success': True,
                            'message': (
                                f"System metrics for {server_name}:\n"
                                f"- CPU: {metrics.get('cpu_usage', 'Unknown')}%\n"
                                f"- Memory: {metrics.get('memory_percent', 'Unknown')}% "
                                f"({metrics.get('memory_used', 'Unknown')}MB / {metrics.get('memory_total', 'Unknown')}MB)\n"
                                f"- Disk: {metrics.get('disk_percent', 'Unknown')}%\n"
                                f"- Load: {metrics.get('load_1', 'Unknown')} (1m), "
                                f"{metrics.get('load_5', 'Unknown')} (5m), "
                                f"{metrics.get('load_15', 'Unknown')} (15m)"
                            ),
                            'data': metrics
                        })
                    else:
                        results.append({
                            'server': server_name,
                            'success': False,
                            'message': f"Failed to get metrics from {server_name}",
                            'error': metrics.get('error', 'Unknown error')
                        })
            
            elif intent == 'command':
                # Execute command on server
                command_result = ssh_manager.execute_command(server_id, action)
                
                # Log command to history
                db.add_command_history(
                    server_id=server_id,
                    command=action,
                    output=command_result.get('stdout', '') + '\n' + command_result.get('stderr', ''),
                    exit_code=command_result.get('exit_code')
                )
                
                if command_result['success']:
                    results.append({
                        'server': server_name,
                        'success': True,
                        'message': f"Command executed successfully on {server_name}",
                        'data': {
                            'command': action,
                            'stdout': command_result.get('stdout', ''),
                            'stderr': command_result.get('stderr', ''),
                            'exit_code': command_result.get('exit_code')
                        }
                    })
                else:
                    results.append({
                        'server': server_name,
                        'success': False,
                        'message': f"Failed to execute command on {server_name}",
                        'error': command_result.get('stderr', command_result.get('error', 'Unknown error')),
                        'data': {
                            'command': action,
                            'exit_code': command_result.get('exit_code')
                        }
                    })
        
        # Compile the overall response
        overall_success = all(result['success'] for result in results)
        
        if len(results) == 1:
            # For single server, simplify the response
            response = results[0]
            response['parsed_intent'] = parsed_intent
            return jsonify(response), 200 if response['success'] else 500
        else:
            # For multiple servers, return aggregate response
            return jsonify({
                'success': overall_success,
                'message': f"Processed query across {len(results)} servers",
                'parsed_intent': parsed_intent,
                'results': results
            }), 200 if overall_success else 500
            
    except Exception as e:
        logger.error(f"Error processing natural language query: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f"Error processing query: {str(e)}"
        }), 500 