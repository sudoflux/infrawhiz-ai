import os
<<<<<<< HEAD
import logging
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
import db
from routes import api
from websocket import socketio, init_socketio
=======
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from server_manager import ServerManager
from ai_agent import AIAgent
>>>>>>> origin/main

# Load environment variables
load_dotenv()

<<<<<<< HEAD
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='frontend/build' if os.path.exists('frontend/build') else None,
                static_url_path='')
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Initialize WebSocket
    init_socketio(app)
    
    # Serve frontend if available
    @app.route('/')
    def index():
        if app.static_folder:
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({
                'message': 'InfraWhiz API Server',
                'status': 'running',
                'endpoints': [
                    '/api/servers',
                    '/api/servers/<server_id>',
                    '/api/servers/<server_id>/command',
                    '/api/servers/<server_id>/metrics',
                    '/api/command/history',
                    '/api/process'
                ]
            })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Route not found'}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Initialize database
    db.init_db()
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    # Run with SocketIO instead of plain Flask
    logger.info(f"Starting InfraWhiz on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=app.config['DEBUG']) 
=======
app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
socketio = SocketIO(app, cors_allowed_origins='*')

# Initialize server manager and AI agent
server_manager = ServerManager()
ai_agent = AIAgent(server_manager)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/servers', methods=['GET'])
def get_servers():
    return jsonify(server_manager.list_servers())

@app.route('/api/servers', methods=['POST'])
def add_server():
    data = request.json
    server = server_manager.add_server(
        name=data['name'],
        hostname=data['hostname'],
        username=data['username'],
        password=data.get('password'),
        key_path=data.get('key_path'),
        port=data.get('port', 22)
    )
    return jsonify(server)

@app.route('/api/servers/<server_id>', methods=['DELETE'])
def remove_server(server_id):
    server_manager.remove_server(server_id)
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('user_message')
def handle_message(data):
    user_input = data['message']
    
    # Process the user input through Claude
    response = ai_agent.process_input(user_input)
    
    # Send response back to the client
    emit('ai_response', {'message': response['message'], 'actions': response.get('actions', [])})

@socketio.on('execute_action')
def execute_action(data):
    action = data['action']
    server_id = data['server_id']
    command = data['command']
    
    # Execute the command on the server
    result = server_manager.execute_command(server_id, command)
    
    # Send result back to the client
    emit('action_result', {'action': action, 'server_id': server_id, 'result': result})

@socketio.on('get_metrics')
def get_metrics(data):
    server_id = data['server_id']
    metrics = server_manager.get_metrics(server_id)
    emit('metrics_update', {'server_id': server_id, 'metrics': metrics})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
>>>>>>> origin/main
