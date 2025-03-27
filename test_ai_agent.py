#!/usr/bin/env python3

import unittest
import sys
import os
from ai_agent import AIAgent

class TestAIAgent(unittest.TestCase):
    """Test cases for the AIAgent class, specifically for the parse_user_input function."""
    
    def setUp(self):
        """Set up the test case with a fresh AIAgent instance."""
        self.agent = AIAgent()
    
    def test_cpu_metrics_query(self):
        """Test CPU metrics query parsing."""
        result = self.agent.parse_user_input("What's the CPU usage on server1?")
        self.assertEqual(result["intent"], "metrics")
        self.assertEqual(result["target_server"], "server1")
        self.assertEqual(result["action"], "cpu")
    
    def test_memory_metrics_query(self):
        """Test memory metrics query parsing."""
        result = self.agent.parse_user_input("Show me memory usage on server2")
        self.assertEqual(result["intent"], "metrics")
        self.assertEqual(result["target_server"], "server2")
        self.assertEqual(result["action"], "memory")
    
    def test_disk_space_query(self):
        """Test disk space query parsing."""
        result = self.agent.parse_user_input("Check disk space on all servers")
        self.assertEqual(result["intent"], "metrics")
        self.assertEqual(result["target_server"], "all")
        self.assertEqual(result["action"], "disk")
    
    def test_restart_service_command(self):
        """Test service restart command parsing."""
        result = self.agent.parse_user_input("Restart nginx on server2")
        self.assertEqual(result["intent"], "command")
        self.assertEqual(result["target_server"], "server2")
        self.assertEqual(result["action"], "systemctl restart nginx")
    
    def test_check_service_status(self):
        """Test service status command parsing."""
        result = self.agent.parse_user_input("Check status of apache2 on server1")
        self.assertEqual(result["intent"], "command")
        self.assertEqual(result["target_server"], "server1")
        self.assertEqual(result["action"], "systemctl status apache2")
    
    def test_list_processes(self):
        """Test process listing command parsing."""
        result = self.agent.parse_user_input("List processes on server3")
        self.assertEqual(result["intent"], "command")
        self.assertEqual(result["target_server"], "server3")
        self.assertEqual(result["action"], "ps aux | head -10")
    
    def test_direct_command(self):
        """Test direct command parsing."""
        result = self.agent.parse_user_input("Run ls -la /var/log on server1")
        self.assertEqual(result["intent"], "command")
        self.assertEqual(result["target_server"], "server1")
        self.assertEqual(result["action"], "ls -la /var/log")
    
    def test_all_servers(self):
        """Test 'all servers' parsing."""
        result = self.agent.parse_user_input("Check disk space on all servers")
        self.assertEqual(result["target_server"], "all")
    
    def test_implicit_metric(self):
        """Test implicit metric detection."""
        result = self.agent.parse_user_input("How is the CPU doing on server1?")
        self.assertEqual(result["intent"], "metrics")
        self.assertEqual(result["action"], "cpu")
    
    def test_different_server_formats(self):
        """Test different server reference formats."""
        # Test "on server X" format
        result = self.agent.parse_user_input("Check CPU on server webserver")
        self.assertEqual(result["target_server"], "webserver")
        
        # Test "on X server" format
        result = self.agent.parse_user_input("Check CPU on webserver server")
        self.assertEqual(result["target_server"], "webserver")
        
        # Test "X's" format
        result = self.agent.parse_user_input("Check webserver's CPU")
        self.assertEqual(result["target_server"], "webserver")
    
    def test_fallback_behavior(self):
        """Test fallback behavior when no clear intent is provided."""
        result = self.agent.parse_user_input("How is server1 doing?")
        self.assertEqual(result["intent"], "metrics")
        self.assertEqual(result["action"], "general")
        self.assertEqual(result["target_server"], "server1")
        
if __name__ == "__main__":
    unittest.main() 