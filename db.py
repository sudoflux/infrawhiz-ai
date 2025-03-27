import os
import sqlite3
import uuid
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager

# Database file path
DB_PATH = os.environ.get('DB_PATH', 'infrawhiz.db')

def init_db():
    """Initialize the database with necessary tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Create servers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            hostname TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT,
            key_path TEXT,
            port INTEGER DEFAULT 22,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create command_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_history (
            id TEXT PRIMARY KEY,
            server_id TEXT NOT NULL,
            command TEXT NOT NULL,
            output TEXT,
            exit_code INTEGER,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id)
        )
        ''')
        
        conn.commit()

@contextmanager
def get_connection():
    """Get a database connection with context management."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()

# Server management functions
def add_server(name: str, hostname: str, username: str, 
               password: Optional[str] = None, 
               key_path: Optional[str] = None, 
               port: int = 22) -> Dict[str, Any]:
    """Add a server to the database."""
    server_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO servers (id, name, hostname, username, password, key_path, port) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (server_id, name, hostname, username, password, key_path, port)
        )
        conn.commit()
    
    return {
        'id': server_id,
        'name': name,
        'hostname': hostname,
        'username': username,
        'port': port
    }

def get_server(server_id: str) -> Optional[Dict[str, Any]]:
    """Get a server by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM servers WHERE id = ?', (server_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None

def get_servers() -> List[Dict[str, Any]]:
    """Get all servers."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, hostname, username, port FROM servers')
        return [dict(row) for row in cursor.fetchall()]

def update_server(server_id: str, **kwargs) -> bool:
    """Update server details."""
    valid_fields = {'name', 'hostname', 'username', 'password', 'key_path', 'port'}
    update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
    
    if not update_fields:
        return False
    
    set_clause = ', '.join(f"{field} = ?" for field in update_fields)
    values = list(update_fields.values())
    values.append(server_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'UPDATE servers SET {set_clause} WHERE id = ?',
            values
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_server(server_id: str) -> bool:
    """Delete a server."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM servers WHERE id = ?', (server_id,))
        conn.commit()
        return cursor.rowcount > 0

# Command history functions
def add_command_history(server_id: str, command: str, 
                       output: Optional[str] = None, 
                       exit_code: Optional[int] = None) -> str:
    """Add a command execution record to history."""
    command_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO command_history (id, server_id, command, output, exit_code) '
            'VALUES (?, ?, ?, ?, ?)',
            (command_id, server_id, command, output, exit_code)
        )
        conn.commit()
    
    return command_id

def get_command_history(server_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Get command history, optionally filtered by server_id."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        if server_id:
            cursor.execute(
                'SELECT * FROM command_history WHERE server_id = ? ORDER BY executed_at DESC LIMIT ?',
                (server_id, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM command_history ORDER BY executed_at DESC LIMIT ?',
                (limit,)
            )
            
        return [dict(row) for row in cursor.fetchall()]

# Initialize the database on module load
init_db() 