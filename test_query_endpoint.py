#!/usr/bin/env python3

import requests
import sys
import json
import argparse

def test_query_endpoint(host, query, verbose=False):
    """
    Test the natural language query endpoint by sending a request and displaying the response.
    
    Args:
        host: The hostname/IP and port of the InfraWhiz server (e.g., http://localhost:5000)
        query: The natural language query to send (e.g., "Check CPU usage on server1")
        verbose: Whether to display the full response or just a summary
    """
    endpoint = f"{host}/api/query"
    
    # Prepare payload
    payload = {
        "input": query
    }
    
    print(f"🚀 Sending query: \"{query}\"")
    print(f"📡 Endpoint: {endpoint}")
    
    try:
        # Send request
        response = requests.post(endpoint, json=payload)
        
        # Check response status
        if response.status_code >= 200 and response.status_code < 300:
            print(f"✅ Request successful (Status: {response.status_code})")
        else:
            print(f"❌ Request failed (Status: {response.status_code})")
        
        # Parse response
        try:
            data = response.json()
            
            # Display parsed intent
            if 'parsed_intent' in data:
                intent = data['parsed_intent']
                print("\n📋 Parsed Intent:")
                print(f"   Intent: {intent.get('intent', 'Unknown')}")
                print(f"   Target Server: {intent.get('target_server', 'Unknown')}")
                print(f"   Action: {intent.get('action', 'Unknown')}")
            
            # Display message
            if 'message' in data:
                print(f"\n💬 Message: {data['message']}")
            
            # Display results
            if 'results' in data:
                print("\n📊 Results:")
                for i, result in enumerate(data['results'], 1):
                    server = result.get('server', 'Unknown')
                    success = result.get('success', False)
                    message = result.get('message', '')
                    
                    status_icon = "✅" if success else "❌"
                    print(f"   {status_icon} Server {server}: {message}")
            
            # Display data for single server result
            elif 'data' in data and verbose:
                print("\n📊 Data:")
                if 'command' in data.get('data', {}):
                    print(f"   Command: {data['data'].get('command', '')}")
                    print(f"   Exit Code: {data['data'].get('exit_code', '')}")
                    
                    # Display stdout/stderr
                    stdout = data['data'].get('stdout', '')
                    stderr = data['data'].get('stderr', '')
                    
                    if stdout:
                        print("\n📤 Standard Output:")
                        print("   " + "\n   ".join(stdout.strip().split("\n")))
                    
                    if stderr:
                        print("\n📥 Standard Error:")
                        print("   " + "\n   ".join(stderr.strip().split("\n")))
                else:
                    # Display metrics data
                    for key, value in data.get('data', {}).items():
                        print(f"   {key}: {value}")
            
            # Display full response in verbose mode
            if verbose:
                print("\n🔍 Full Response:")
                print(json.dumps(data, indent=2))
            
        except json.JSONDecodeError:
            print("❌ Could not parse response as JSON")
            print(response.text)
    
    except requests.RequestException as e:
        print(f"❌ Request error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the InfraWhiz natural language query endpoint")
    parser.add_argument("--host", default="http://localhost:5000", help="Host address (default: http://localhost:5000)")
    parser.add_argument("--query", required=True, help="Natural language query to send")
    parser.add_argument("--verbose", "-v", action="store_true", help="Display verbose output")
    
    args = parser.parse_args()
    
    test_query_endpoint(args.host, args.query, args.verbose) 