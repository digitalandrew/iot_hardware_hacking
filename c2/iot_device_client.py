#!/usr/bin/env python3

import requests
import subprocess
import time
import json

SERVER_URL = "http://localhost:5000"
POLL_INTERVAL = 5  # seconds

def execute_command(command):
    """Execute a system command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output.strip() if output.strip() else f"Command completed (exit code: {result.returncode})"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def poll_for_command():
    """Poll the server for a new command"""
    try:
        response = requests.get(f"{SERVER_URL}/command", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('command', '').strip()
    except Exception as e:
        print(f"Error polling for command: {e}")
    return None

def submit_response(command, response):
    """Submit command response to the server"""
    try:
        payload = {
            'command': command,
            'response': response
        }
        resp = requests.post(f"{SERVER_URL}/response", json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"Response submitted successfully for command: {command[:50]}...")
        else:
            print(f"Failed to submit response: {resp.status_code}")
    except Exception as e:
        print(f"Error submitting response: {e}")

def main():
    print("IoT Device Client Starting...")
    print(f"Server: {SERVER_URL}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("Press Ctrl+C to stop")
    
    last_command = ""
    
    try:
        while True:
            # Poll for command
            command = poll_for_command()
            
            if command and command != last_command:
                print(f"\nReceived command: {command}")
                
                # Execute the command
                response = execute_command(command)
                print(f"Command output: {response[:100]}{'...' if len(response) > 100 else ''}")
                
                # Submit response
                submit_response(command, response)
                
                last_command = command
            
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nShutting down IoT device client...")

if __name__ == '__main__':
    main()