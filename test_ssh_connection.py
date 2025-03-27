#!/usr/bin/env python3

import os
import argparse
from ssh_manager import SSHManager

def test_ssh_connection(hostname, username, password=None, key_path=None, port=22):
    """
    Test SSH connection to a remote server using the SSHManager class.
    
    Args:
        hostname: Remote server hostname or IP address
        username: SSH username
        password: SSH password (optional if key_path is provided)
        key_path: Path to private key file (optional if password is provided)
        port: SSH port (default: 22)
    """
    print(f"Testing SSH connection to {hostname}:{port} as {username}")
    
    # Create a new SSHManager instance
    ssh = SSHManager()
    
    # Generate a test server ID
    server_id = "test_connection"
    
    # Attempt to establish connection
    print("Attempting to connect...")
    connection_result = ssh.connect(
        server_id=server_id,
        hostname=hostname,
        username=username,
        password=password,
        key_path=key_path,
        port=port
    )
    
    if not connection_result:
        print("❌ Connection failed!")
        return
    
    print("✅ Connection established successfully!")
    
    # Test basic command execution
    print("\nExecuting 'uptime' command...")
    result = ssh.execute_command(server_id, "uptime")
    
    if result['success']:
        print("✅ Command executed successfully!")
        print(f"Output: {result['stdout'].strip()}")
    else:
        print("❌ Command execution failed!")
        print(f"Error: {result.get('error', result.get('stderr', 'Unknown error'))}")
    
    # Test system metrics collection
    print("\nCollecting system metrics...")
    metrics = ssh.get_server_metrics(server_id)
    
    if metrics['success']:
        print("✅ Metrics collected successfully!")
        print("CPU Usage: {:.1f}%".format(metrics.get('cpu_usage', 0)))
        print("Memory: {}/{} MB ({:.1f}%)".format(
            metrics.get('memory_used', 0),
            metrics.get('memory_total', 0),
            metrics.get('memory_percent', 0)
        ))
        print("Disk Usage: {}".format(metrics.get('disk_percent', 0)))
        print("Load Average: {} (1m), {} (5m), {} (15m)".format(
            metrics.get('load_1', 0),
            metrics.get('load_5', 0),
            metrics.get('load_15', 0)
        ))
    else:
        print("❌ Metrics collection failed!")
        print(f"Error: {metrics.get('error', 'Unknown error')}")
    
    # Disconnect
    print("\nDisconnecting...")
    ssh.disconnect(server_id)
    print("✅ Disconnected")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test SSH connection using SSHManager")
    parser.add_argument("--host", required=True, help="Hostname or IP address")
    parser.add_argument("--user", required=True, help="SSH username")
    parser.add_argument("--password", help="SSH password (omit if using key)")
    parser.add_argument("--key", help="Path to SSH private key file")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    
    args = parser.parse_args()
    
    if not args.password and not args.key:
        parser.error("Either --password or --key must be provided")
    
    test_ssh_connection(
        hostname=args.host,
        username=args.user,
        password=args.password,
        key_path=args.key,
        port=args.port
    ) 