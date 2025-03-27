import os
import paramiko
import time
import threading
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSHManager:
    def __init__(self):
        self.connections = {}  # Dictionary to store active SSH connections
        self.lock = threading.Lock()  # Lock for thread safety
    
    def connect(self, server_id: str, hostname: str, username: str, 
                password: Optional[str] = None, key_path: Optional[str] = None, 
                port: int = 22) -> bool:
        """Establish an SSH connection to a server and store it."""
        try:
            # Create a new SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect using either password or key
            if key_path and os.path.exists(key_path):
                private_key = paramiko.RSAKey.from_private_key_file(key_path)
                client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    pkey=private_key,
                    timeout=10
                )
            elif password:
                client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            else:
                logger.error(f"No valid authentication method provided for {hostname}")
                return False
                
            # Store the connection
            with self.lock:
                if server_id in self.connections:
                    # Close existing connection if present
                    self.disconnect(server_id)
                self.connections[server_id] = {
                    'client': client,
                    'last_used': time.time()
                }
            
            logger.info(f"Successfully connected to {hostname}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {hostname}: {str(e)}")
            return False
    
    def disconnect(self, server_id: str) -> bool:
        """Close an SSH connection."""
        with self.lock:
            if server_id in self.connections:
                try:
                    self.connections[server_id]['client'].close()
                    del self.connections[server_id]
                    return True
                except Exception as e:
                    logger.error(f"Error disconnecting from server {server_id}: {str(e)}")
            return False
    
    def get_connection(self, server_id: str) -> Optional[paramiko.SSHClient]:
        """Get an active SSH connection or None if not connected."""
        with self.lock:
            if server_id in self.connections:
                # Update last used time
                self.connections[server_id]['last_used'] = time.time()
                return self.connections[server_id]['client']
            return None
    
    def execute_command(self, server_id: str, command: str, 
                        timeout: int = 30) -> Dict[str, Any]:
        """Execute a command on the connected server."""
        client = self.get_connection(server_id)
        
        if not client:
            return {
                'success': False,
                'error': 'Not connected to server',
                'stdout': '',
                'stderr': 'SSH connection not established',
                'exit_code': -1
            }
        
        try:
            # Execute the command
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            
            # Read output
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            
            return {
                'success': exit_code == 0,
                'stdout': stdout_data,
                'stderr': stderr_data,
                'exit_code': exit_code
            }
            
        except Exception as e:
            logger.error(f"Error executing command on server {server_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': f'Error: {str(e)}',
                'exit_code': -1
            }
    
    def get_server_metrics(self, server_id: str) -> Dict[str, Any]:
        """Collect basic metrics from the server."""
        metrics = {
            'success': False,
            'timestamp': time.time()
        }
        
        # Commands to collect metrics
        commands = {
            'cpu': "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'",
            'memory': "free -m | grep Mem | awk '{print $3,$2}'",
            'disk': "df -h / | tail -1 | awk '{print $3,$2,$5}'",
            'load': "cat /proc/loadavg | awk '{print $1,$2,$3}'",
            'uptime': "uptime -p",
            'network': "cat /proc/net/dev | grep -v lo | grep ':' | awk '{print $1, $2, $10}' | head -1"
        }
        
        client = self.get_connection(server_id)
        if not client:
            metrics['error'] = 'Not connected to server'
            return metrics
        
        try:
            # CPU usage
            result = self.execute_command(server_id, commands['cpu'])
            if result['success']:
                metrics['cpu_usage'] = float(result['stdout'].strip())
            
            # Memory usage
            result = self.execute_command(server_id, commands['memory'])
            if result['success']:
                used, total = map(int, result['stdout'].strip().split())
                metrics['memory_used'] = used
                metrics['memory_total'] = total
                metrics['memory_percent'] = round(used / total * 100, 1)
            
            # Disk usage
            result = self.execute_command(server_id, commands['disk'])
            if result['success']:
                used, total, percent = result['stdout'].strip().split()
                metrics['disk_used'] = used
                metrics['disk_total'] = total
                metrics['disk_percent'] = float(percent.replace('%', ''))
            
            # Load average
            result = self.execute_command(server_id, commands['load'])
            if result['success']:
                load1, load5, load15 = map(float, result['stdout'].strip().split())
                metrics['load_1'] = load1
                metrics['load_5'] = load5
                metrics['load_15'] = load15
            
            # Uptime
            result = self.execute_command(server_id, commands['uptime'])
            if result['success']:
                metrics['uptime'] = result['stdout'].strip()
            
            # Network
            result = self.execute_command(server_id, commands['network'])
            if result['success'] and result['stdout'].strip():
                interface, rx, tx = result['stdout'].strip().split()
                metrics['network_interface'] = interface.replace(':', '')
                metrics['network_rx'] = int(rx)
                metrics['network_tx'] = int(tx)
            
            metrics['success'] = True
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics from server {server_id}: {str(e)}")
            metrics['error'] = str(e)
            return metrics
    
    def cleanup_idle_connections(self, max_idle_time: int = 600) -> int:
        """Close connections that have been idle for too long."""
        current_time = time.time()
        closed_count = 0
        
        with self.lock:
            server_ids = list(self.connections.keys())
            
            for server_id in server_ids:
                last_used = self.connections[server_id]['last_used']
                if current_time - last_used > max_idle_time:
                    if self.disconnect(server_id):
                        closed_count += 1
        
        return closed_count

    def upload_file(self, server_id: str, local_path: str, 
                   remote_path: str) -> Dict[str, Any]:
        """Upload a file to the remote server."""
        client = self.get_connection(server_id)
        
        if not client:
            return {
                'success': False,
                'error': 'Not connected to server'
            }
        
        try:
            # Open SFTP session
            sftp = client.open_sftp()
            
            # Upload the file
            sftp.put(local_path, remote_path)
            
            # Close SFTP session
            sftp.close()
            
            return {
                'success': True,
                'local_path': local_path,
                'remote_path': remote_path
            }
            
        except Exception as e:
            logger.error(f"Error uploading file to server {server_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'local_path': local_path,
                'remote_path': remote_path
            }
    
    def download_file(self, server_id: str, remote_path: str, 
                     local_path: str) -> Dict[str, Any]:
        """Download a file from the remote server."""
        client = self.get_connection(server_id)
        
        if not client:
            return {
                'success': False,
                'error': 'Not connected to server'
            }
        
        try:
            # Open SFTP session
            sftp = client.open_sftp()
            
            # Download the file
            sftp.get(remote_path, local_path)
            
            # Close SFTP session
            sftp.close()
            
            return {
                'success': True,
                'local_path': local_path,
                'remote_path': remote_path
            }
            
        except Exception as e:
            logger.error(f"Error downloading file from server {server_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'local_path': local_path,
                'remote_path': remote_path
            }

# Create a singleton instance
ssh_manager = SSHManager() 