import os
import json
import uuid
import time
import sqlite3
import paramiko
from paramiko.ssh_exception import SSHException

class ServerManager:
    def __init__(self, db_path='infrawhiz.db'):
        self.db_path = db_path
        self.servers = {}
        self.connections = {}
        self._init_db()
        self._load_servers()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            hostname TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT,
            key_path TEXT,
            port INTEGER DEFAULT 22
        )
        ''')
        conn.commit()
        conn.close()

    def _load_servers(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, hostname, username, password, key_path, port FROM servers')
        servers = cursor.fetchall()
        conn.close()

        for server in servers:
            server_id, name, hostname, username, password, key_path, port = server
            self.servers[server_id] = {
                'id': server_id,
                'name': name,
                'hostname': hostname,
                'username': username,
                'password': password,
                'key_path': key_path,
                'port': port
            }

    def add_server(self, name, hostname, username, password=None, key_path=None, port=22):
        server_id = str(uuid.uuid4())
        server = {
            'id': server_id,
            'name': name,
            'hostname': hostname,
            'username': username,
            'password': password,
            'key_path': key_path,
            'port': port
        }
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO servers (id, name, hostname, username, password, key_path, port) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (server_id, name, hostname, username, password, key_path, port)
        )
        conn.commit()
        conn.close()
        
        # Add to in-memory dict
        self.servers[server_id] = server
        
        return {'id': server_id, 'name': name, 'hostname': hostname, 'username': username, 'port': port}

    def remove_server(self, server_id):
        if server_id in self.connections:
            self.disconnect(server_id)
            
        if server_id in self.servers:
            # Remove from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM servers WHERE id = ?', (server_id,))
            conn.commit()
            conn.close()
            
            # Remove from in-memory dict
            del self.servers[server_id]
            return True
        return False

    def list_servers(self):
        return [
            {'id': s['id'], 'name': s['name'], 'hostname': s['hostname'], 'username': s['username'], 'port': s['port']}
            for s in self.servers.values()
        ]

    def _get_connection(self, server_id):
        # Return existing connection if it exists
        if server_id in self.connections:
            return self.connections[server_id]
            
        # Otherwise create a new connection
        if server_id not in self.servers:
            raise ValueError(f"Server with ID {server_id} not found")
            
        server = self.servers[server_id]
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if server['key_path']:
                key = paramiko.RSAKey.from_private_key_file(server['key_path'])
                client.connect(
                    hostname=server['hostname'],
                    port=server['port'],
                    username=server['username'],
                    pkey=key,
                    timeout=10
                )
            else:
                client.connect(
                    hostname=server['hostname'],
                    port=server['port'],
                    username=server['username'],
                    password=server['password'],
                    timeout=10
                )
                
            self.connections[server_id] = client
            return client
        except Exception as e:
            raise ConnectionError(f"Failed to connect to server: {str(e)}")

    def disconnect(self, server_id):
        if server_id in self.connections:
            self.connections[server_id].close()
            del self.connections[server_id]
            return True
        return False

    def execute_command(self, server_id, command):
        try:
            client = self._get_connection(server_id)
            stdin, stdout, stderr = client.exec_command(command, timeout=30)
            return {
                'stdout': stdout.read().decode('utf-8'),
                'stderr': stderr.read().decode('utf-8'),
                'exit_code': stdout.channel.recv_exit_status()
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': f"Error executing command: {str(e)}",
                'exit_code': -1
            }

    def get_metrics(self, server_id):
        # Basic metrics collection using shell commands
        metrics = {}
        
        try:
            # CPU usage
            cpu_result = self.execute_command(server_id, "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'")
            if cpu_result['exit_code'] == 0:
                metrics['cpu_usage'] = float(cpu_result['stdout'].strip())
            
            # Memory usage
            mem_result = self.execute_command(server_id, "free -m | grep Mem | awk '{print $3,$2}'")
            if mem_result['exit_code'] == 0:
                used, total = map(int, mem_result['stdout'].strip().split())
                metrics['memory_used'] = used
                metrics['memory_total'] = total
                metrics['memory_percent'] = round(used / total * 100, 1)
            
            # Disk usage
            disk_result = self.execute_command(server_id, "df -h / | tail -1 | awk '{print $3,$2,$5}'")
            if disk_result['exit_code'] == 0:
                used, total, percent = disk_result['stdout'].strip().split()
                metrics['disk_used'] = used
                metrics['disk_total'] = total
                metrics['disk_percent'] = float(percent.replace('%', ''))
            
            # Load average
            load_result = self.execute_command(server_id, "cat /proc/loadavg | awk '{print $1,$2,$3}'")
            if load_result['exit_code'] == 0:
                load1, load5, load15 = map(float, load_result['stdout'].strip().split())
                metrics['load_1'] = load1
                metrics['load_5'] = load5
                metrics['load_15'] = load15
            
            # Uptime
            uptime_result = self.execute_command(server_id, "uptime -p")
            if uptime_result['exit_code'] == 0:
                metrics['uptime'] = uptime_result['stdout'].strip()
            
            # Network
            net_result = self.execute_command(
                server_id, 
                "cat /proc/net/dev | grep -v lo | grep ':' | awk '{print $1, $2, $10}' | head -1"
            )
            if net_result['exit_code'] == 0 and net_result['stdout'].strip():
                interface, rx, tx = net_result['stdout'].strip().split()
                metrics['network_interface'] = interface.replace(':', '')
                metrics['network_rx'] = int(rx)
                metrics['network_tx'] = int(tx)
            
            metrics['timestamp'] = time.time()
            return metrics
        except Exception as e:
            return {'error': str(e)}