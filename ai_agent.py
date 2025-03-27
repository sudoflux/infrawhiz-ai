import os
import re
import json
<<<<<<< HEAD
import logging
from typing import Dict, List, Any, Optional
import db
from ssh_manager import ssh_manager

# Later we'll integrate with Claude
# from anthropic import Anthropic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        # List of potentially destructive commands
=======
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    def __init__(self, server_manager):
        self.server_manager = server_manager
        self.client = anthropic.Anthropic(api_key=os.environ.get('CLAUDE_API_KEY'))
>>>>>>> origin/main
        self.destructive_commands = [
            'rm', 'rmdir', 'mkfs', 'dd', 'shutdown', 'reboot', 'halt', 'poweroff',
            'kill', 'killall', 'systemctl stop', 'systemctl restart', 'service',
            'fdisk', 'mkswap', 'mkfs', 'format', 'parted', 'gparted', 'lvremove',
            'vgremove', 'pvremove'
        ]
<<<<<<< HEAD
        
        # Command patterns for common tasks
        self.command_patterns = {
            'cpu_usage': {
                'pattern': r'(cpu|processor|load|usage)',
                'command': "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'",
                'explanation': "Checking CPU usage"
            },
            'memory_usage': {
                'pattern': r'(memory|ram|mem|\bmem\b)',
                'command': "free -h",
                'explanation': "Checking memory usage"
            },
            'disk_usage': {
                'pattern': r'(disk|storage|space|drive|filesystem|fs)',
                'command': "df -h",
                'explanation': "Checking disk usage"
            },
            'system_info': {
                'pattern': r'(system|info|information|details|specs|hardware)',
                'command': "uname -a && lscpu | grep 'Model name'",
                'explanation': "Getting system information"
            },
            'list_processes': {
                'pattern': r'(process|processes|running|task|tasks)',
                'command': "ps aux | sort -nrk 3,3 | head -n 10",
                'explanation': "Listing top CPU-consuming processes"
            },
            'check_service': {
                'pattern': r'(service|status)\s+(\w+)',
                'command': "systemctl status {service}",
                'explanation': "Checking status of {service}"
            },
            'restart_service': {
                'pattern': r'restart\s+(\w+)',
                'command': "systemctl restart {service}",
                'explanation': "Restarting {service}",
                'destructive': True
            }
        }
        
        # Initialize Claude client (placeholder for now)
        # self.client = Anthropic(api_key=os.environ.get('CLAUDE_API_KEY'))
    
    def parse_user_input(self, input_text: str) -> dict:
        """
        Parse natural language input and extract intent, target server, and requested action.
        
        Args:
            input_text: Natural language text input from the user.
            
        Returns:
            Dictionary with keys:
                - intent: "metrics" or "command"
                - target_server: Server name or "all"
                - action: Specific metric, command, or action to perform
        """
        # Initialize the result dictionary
        result = {
            "intent": None,
            "target_server": None,
            "action": None
        }
        
        # Convert to lowercase for easier pattern matching
        text = input_text.lower()
        
        # Extract target server
        server_patterns = [
            r'(?:on|for|in|at)\s+(?:server\s*)?([a-zA-Z0-9_-]+)',  # "on server1" or "on server server1"
            r'([a-zA-Z0-9_-]+)(?:\s+server)(?:\'s|\s|$)',          # "server1 server" or "server1's"
            r'([a-zA-Z0-9_-]+)(?:\'s|\s+)(?:system|machine)'       # "server1's system" or "server1 machine"
        ]
        
        for pattern in server_patterns:
            match = re.search(pattern, text)
            if match:
                server_name = match.group(1)
                # Check if it's referring to all servers
                if server_name in ['all', 'every', 'each', 'any']:
                    result["target_server"] = "all"
                else:
                    result["target_server"] = server_name
                break
        
        # If no server specified explicitly, look for "all servers" pattern
        if not result["target_server"] and re.search(r'all\s+servers', text):
            result["target_server"] = "all"
            
        # Default to first available server if none specified
        if not result["target_server"]:
            servers = db.get_servers()
            if servers and len(servers) == 1:
                result["target_server"] = servers[0]['name']
            else:
                # If multiple servers and none specified, default behavior
                result["target_server"] = "all"
        
        # Determine intent and action
        # Check for metrics intent
        metrics_patterns = {
            'cpu': r'(?:cpu|processor|load)\s+(?:usage|utilization|load|stat)',
            'memory': r'(?:memory|ram|mem)\s+(?:usage|utilization|stat)',
            'disk': r'(?:disk|storage|space|drive|filesystem)\s+(?:usage|utilization|free|available|stat)',
            'uptime': r'(?:uptime|how long|running time)',
            'network': r'(?:network|bandwidth|connection|internet)\s+(?:usage|speed|stat)',
            'general': r'(?:status|health|metrics|statistics|stats|performance|monitor)'
        }
        
        for metric, pattern in metrics_patterns.items():
            if re.search(pattern, text):
                result["intent"] = "metrics"
                result["action"] = metric
                break
        
        # If not a metrics request, check for command intent
        if not result["intent"]:
            # Service restart pattern
            restart_match = re.search(r'restart\s+(\w+)', text)
            if restart_match:
                service = restart_match.group(1)
                result["intent"] = "command"
                result["action"] = f"systemctl restart {service}"
                return result
            
            # Service status pattern
            status_match = re.search(r'(?:status|check)\s+(?:of\s+)?(\w+)', text)
            if status_match:
                service = status_match.group(1)
                result["intent"] = "command"
                result["action"] = f"systemctl status {service}"
                return result
            
            # Specific command patterns
            command_patterns = [
                # File listing
                (r'(?:list|show|display)\s+(?:files|directories)', "ls -la"),
                # Process listing
                (r'(?:list|show|display)\s+(?:process|processes)', "ps aux | head -10"),
                # Disk space
                (r'(?:check|show|display)\s+disk\s+space', "df -h"),
                # Memory usage
                (r'(?:check|show|display)\s+memory\s+usage', "free -h"),
                # User listing
                (r'(?:list|show|display)\s+users', "who"),
                # Network connections
                (r'(?:list|show|display)\s+(?:network|connections)', "netstat -tuln"),
                # Check logs
                (r'(?:check|view|show|display|tail)\s+logs', "tail -n 20 /var/log/syslog")
            ]
            
            for pattern, cmd in command_patterns:
                if re.search(pattern, text):
                    result["intent"] = "command"
                    result["action"] = cmd
                    return result
            
            # Check for direct command specification
            direct_cmd_match = re.search(r'(?:run|execute|exec)\s+[\'"]?(.+?)[\'"]?(?:\s|$)', text)
            if direct_cmd_match:
                result["intent"] = "command"
                result["action"] = direct_cmd_match.group(1)
                return result
            
            # If still no match, default to generic command based on keywords
            if "cpu" in text:
                result["intent"] = "metrics"
                result["action"] = "cpu"
            elif "memory" in text or "ram" in text:
                result["intent"] = "metrics"
                result["action"] = "memory"
            elif "disk" in text or "space" in text:
                result["intent"] = "metrics"
                result["action"] = "disk"
            elif "process" in text:
                result["intent"] = "command"
                result["action"] = "ps aux | head -10"
            else:
                # Default fallback
                result["intent"] = "metrics"
                result["action"] = "general"
                
        return result
    
    def _is_destructive(self, command: str) -> bool:
        """Check if a command is potentially destructive."""
        return any(cmd in command for cmd in self.destructive_commands)
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process natural language input and determine the action to take."""
        try:
            # When the Claude integration is ready, we'll use it here
            # For now, use simple pattern matching
            parsed_result = self.parse_user_input(user_input)
            
            # Prepare the response structure
            response = {
                'message': '',
                'actions': []
            }
            
            # Get server ID from server name if needed
            server_id = None
            if parsed_result["target_server"]:
                if parsed_result["target_server"] == "all":
                    servers = db.get_servers()
                    if not servers:
                        response['message'] = "No servers are configured. Please add a server first."
                        return response
                    # Will handle "all" servers case in the action handlers
                else:
                    servers = db.get_servers()
                    for server in servers:
                        if server['name'].lower() == parsed_result["target_server"].lower():
                            server_id = server['id']
                            break
                    
                    if not server_id and servers:
                        # If server name not found but servers exist, use the first one as fallback
                        server_id = servers[0]['id']
                        response['message'] = f"Server '{parsed_result['target_server']}' not found. Using default server instead. "
            
            # Handle metrics intent
            if parsed_result["intent"] == "metrics":
                metric_type = parsed_result["action"]
                
                if parsed_result["target_server"] == "all":
                    response['message'] = f"Retrieving {metric_type} metrics for all servers."
                    # Add an action for each server
                    for server in servers:
                        response['actions'].append({
                            'type': 'get_metrics',
                            'server_id': server['id']
                        })
                else:
                    response['message'] = f"Retrieving {metric_type} metrics for {parsed_result['target_server']}."
                    response['actions'].append({
                        'type': 'get_metrics',
                        'server_id': server_id
                    })
            
            # Handle command intent
            elif parsed_result["intent"] == "command":
                command = parsed_result["action"]
                is_destructive = self._is_destructive(command)
                
                if parsed_result["target_server"] == "all":
                    if is_destructive:
                        response['message'] = f"⚠️ Warning: The command '{command}' is potentially destructive. Are you sure you want to run it on all servers?"
                    else:
                        response['message'] = f"Executing '{command}' on all servers."
                    
                    # Add an action for each server
                    for server in servers:
                        if is_destructive:
                            response['actions'].append({
                                'type': 'confirm',
                                'server_id': server['id'],
                                'command': command
                            })
                        else:
                            response['actions'].append({
                                'type': 'execute',
                                'server_id': server['id'],
                                'command': command
                            })
                else:
                    if is_destructive:
                        response['message'] = f"⚠️ Warning: The command '{command}' is potentially destructive. Are you sure you want to run it?"
                        response['actions'].append({
                            'type': 'confirm',
                            'server_id': server_id,
                            'command': command
                        })
                    else:
                        response['message'] = f"Executing '{command}' on {parsed_result['target_server']}."
                        response['actions'].append({
                            'type': 'execute',
                            'server_id': server_id,
                            'command': command
                        })
            
            # No valid intent or action
            else:
                response['message'] = "I'm not sure what you want to do. Try asking about system metrics or specify a command to run."
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return {
                'message': f"I encountered an error processing your request: {str(e)}",
                'actions': []
            }

    def process_command_result(self, command: str, result: Dict[str, Any]) -> str:
        """Format command execution result into a human-readable message."""
        if not result['success']:
            error_message = result.get('error', result.get('stderr', 'Unknown error'))
            return f"Error executing command: {error_message}"
        
        # Basic formatting for common commands
        if "ps aux" in command:
            return f"Top processes:\n\n{result['stdout']}"
        elif "df -h" in command:
            return f"Disk usage:\n\n{result['stdout']}"
        elif "free -h" in command:
            return f"Memory usage:\n\n{result['stdout']}"
        elif "top -bn1" in command and "Cpu" in command:
            cpu_usage = result['stdout'].strip()
            return f"CPU usage: {cpu_usage}%"
        elif "systemctl status" in command:
            service = command.split()[-1]
            if "Active: active" in result['stdout']:
                return f"Service {service} is running."
            else:
                return f"Service {service} status:\n\n{result['stdout']}"
        elif "systemctl restart" in command:
            service = command.split()[-1]
            if result['success']:
                return f"Service {service} has been successfully restarted."
            else:
                return f"Failed to restart service {service}:\n\n{result['stderr']}"
        
        # Generic result formatting
        return result['stdout'] if result['stdout'] else "Command executed successfully with no output."
        
    def format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics into a human-readable message."""
        if not metrics.get('success', False):
            error = metrics.get('error', 'Unknown error')
            return f"Failed to retrieve metrics: {error}"
        
        formatted = "System Metrics:\n\n"
        
        if 'cpu_usage' in metrics:
            formatted += f"• CPU Usage: {metrics['cpu_usage']:.1f}%\n"
        
        if 'memory_used' in metrics and 'memory_total' in metrics:
            formatted += f"• Memory: {metrics['memory_used']} MB / {metrics['memory_total']} MB "
            if 'memory_percent' in metrics:
                formatted += f"({metrics['memory_percent']}%)\n"
            else:
                formatted += "\n"
        
        if 'disk_used' in metrics and 'disk_total' in metrics:
            formatted += f"• Disk: {metrics['disk_used']} / {metrics['disk_total']} "
            if 'disk_percent' in metrics:
                formatted += f"({metrics['disk_percent']}%)\n"
            else:
                formatted += "\n"
        
        if 'load_1' in metrics and 'load_5' in metrics and 'load_15' in metrics:
            formatted += f"• Load Average: {metrics['load_1']} (1m), {metrics['load_5']} (5m), {metrics['load_15']} (15m)\n"
        
        if 'uptime' in metrics:
            formatted += f"• Uptime: {metrics['uptime']}\n"
        
        if 'network_interface' in metrics:
            rx = metrics.get('network_rx', 0)
            tx = metrics.get('network_tx', 0)
            formatted += f"• Network ({metrics['network_interface']}): RX {rx} bytes, TX {tx} bytes\n"
        
        return formatted

# Create a singleton instance
ai_agent = AIAgent() 
=======
    
    def _is_destructive(self, command):
        """Check if a command is potentially destructive"""
        return any(cmd in command for cmd in self.destructive_commands)
    
    def _extract_server_and_command(self, user_input, servers):
        """Extract server name and command from user input"""
        server_names = {server['name'].lower(): server['id'] for server in servers}
        
        # Check for server mention
        found_server_id = None
        server_pattern = r'(?:on|for|at|in)\s+([a-zA-Z0-9_-]+)'
        server_match = re.search(server_pattern, user_input.lower())
        
        if server_match:
            server_name = server_match.group(1).lower()
            if server_name in server_names:
                found_server_id = server_names[server_name]
        
        # If only one server exists, use it as default
        if found_server_id is None and len(servers) == 1:
            found_server_id = servers[0]['id']
            
        return found_server_id
    
    def process_input(self, user_input):
        """Process natural language input with Claude"""
        servers = self.server_manager.list_servers()
        
        if not servers:
            return {
                'message': "No servers are configured. Please add a server first.",
                'actions': []
            }
            
        # Prepare context for Claude
        server_details = "\n".join([f"- {s['name']} ({s['hostname']})" for s in servers])
        
        prompt = f"""
        You are InfraWhiz, an AI assistant for Linux server management. You interpret user requests and convert them into server commands.
        
        Available servers:\n{server_details}
        
        Your goal is to understand what the user wants to do and extract:
        1. Which server they are asking about (default to the first one if unclear)
        2. What command needs to be run (or if metrics should be retrieved)
        3. Whether the command is potentially destructive
        
        The user's request is: "{user_input}"
        
        Respond with a JSON object containing:
        - message: Your human-readable explanation of what you understood and will do
        - action: Either "get_metrics", "run_command", or "none"
        - server_id: The ID of the target server
        - command: If action is "run_command", the shell command to execute
        - destructive: Boolean indicating if the command could cause data loss or service disruption
        
        Do not include any other text in your response, just the JSON.
        """
        
        try:
            # Get a response from Claude
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                system=prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            # Extract and parse the JSON response
            response_json = json.loads(message.content[0].text)
            
            # Handle destructive commands
            if response_json.get('action') == 'run_command' and response_json.get('destructive', False):
                return {
                    'message': f"{response_json['message']}\n\nThis command is potentially destructive. Are you sure you want to proceed?",
                    'actions': [{
                        'type': 'confirm',
                        'server_id': response_json['server_id'],
                        'command': response_json['command']
                    }]
                }
            
            # Handle metrics request
            if response_json.get('action') == 'get_metrics':
                metrics = self.server_manager.get_metrics(response_json['server_id'])
                servers_dict = {s['id']: s['name'] for s in servers}
                server_name = servers_dict.get(response_json['server_id'], 'Unknown')
                
                if 'error' in metrics:
                    return {
                        'message': f"Error retrieving metrics from {server_name}: {metrics['error']}",
                        'actions': []
                    }
                    
                # Format metrics into a readable response
                metric_message = f"Metrics for {server_name}:\n"
                metric_message += f"CPU Usage: {metrics.get('cpu_usage', 'N/A')}%\n"
                metric_message += f"Memory: {metrics.get('memory_used', 'N/A')}MB / {metrics.get('memory_total', 'N/A')}MB ({metrics.get('memory_percent', 'N/A')}%)\n"
                metric_message += f"Disk: {metrics.get('disk_used', 'N/A')} / {metrics.get('disk_total', 'N/A')} ({metrics.get('disk_percent', 'N/A')}%)\n"
                metric_message += f"Load Average: {metrics.get('load_1', 'N/A')} (1m), {metrics.get('load_5', 'N/A')} (5m), {metrics.get('load_15', 'N/A')} (15m)\n"
                metric_message += f"Uptime: {metrics.get('uptime', 'N/A')}"
                
                return {
                    'message': metric_message,
                    'actions': []
                }
                
            # Handle command execution
            if response_json.get('action') == 'run_command':
                return {
                    'message': response_json['message'],
                    'actions': [{
                        'type': 'execute',
                        'server_id': response_json['server_id'],
                        'command': response_json['command']
                    }]
                }
                
            return {
                'message': response_json.get('message', "I'm not sure how to help with that."),
                'actions': []
            }
                
        except Exception as e:
            return {
                'message': f"I encountered an error: {str(e)}",
                'actions': []
            }
>>>>>>> origin/main
