#!/usr/bin/env python3

from flask import Flask, request, jsonify, render_template_string
import datetime
import json

app = Flask(__name__)

# In-memory storage (replace with database in production)
current_command = ""
command_history = []

# Basic HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT Command Control</title>
    <style>
        body { font-family: monospace; margin: 40px; }
        input[type="text"] { width: 400px; padding: 5px; }
        button { padding: 5px 10px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .timestamp { font-size: 12px; color: #666; }
        .command { font-weight: bold; color: #333; }
        .response { background-color: #f9f9f9; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>IoT Device Remote Command Control</h1>
    
    <div>
        <h2>Send New Command</h2>
        <form method="POST" action="/update_command">
            <input type="text" name="command" value="" placeholder="Enter command to execute on device">
            <button type="submit">Update Command</button>
        </form>
        <p><strong>Current Command:</strong> <span class="command">{{ current_command or "None" }}</span></p>
    </div>

    <div>
        <h2>Command History</h2>
        {% if command_history %}
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Command</th>
                <th>Response</th>
            </tr>
            {% for entry in command_history %}
            <tr>
                <td class="timestamp">{{ entry.timestamp }}</td>
                <td class="command">{{ entry.command }}</td>
                <td class="response">{{ entry.response }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No commands executed yet.</p>
        {% endif %}
    </div>

    <script>
        // Auto-refresh every 5 seconds
        setTimeout(function() {
            window.location.reload();
        }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE, 
                                current_command=current_command, 
                                command_history=reversed(command_history[-20:]))  # Show last 20 commands

@app.route('/update_command', methods=['POST'])
def update_command():
    """Update the current command to be sent to devices"""
    global current_command
    current_command = request.form.get('command', '').strip()
    return redirect_to_index()

@app.route('/command', methods=['GET'])
def get_command():
    """Endpoint for IoT devices to poll for commands"""
    return jsonify({'command': current_command})

@app.route('/response', methods=['POST'])
def submit_response():
    """Endpoint for IoT devices to submit command responses"""
    try:
        data = request.get_json()
        if not data or 'command' not in data or 'response' not in data:
            return jsonify({'error': 'Invalid request format. Expected JSON with command and response fields.'}), 400
        
        # Store the response
        entry = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'command': data['command'],
            'response': data['response']
        }
        command_history.append(entry)
        
        # Keep only last 100 entries to prevent memory issues
        if len(command_history) > 100:
            command_history.pop(0)
            
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def redirect_to_index():
    """Helper function to redirect to index page"""
    from flask import redirect, url_for
    return redirect(url_for('index'))

if __name__ == '__main__':
    import socket
    
    # Get all network interfaces
    def get_local_ips():
        ips = []
        # Add localhost
        ips.append('127.0.0.1')
        
        # Get local IP addresses
        try:
            # Connect to a remote address to find local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                if local_ip not in ips:
                    ips.append(local_ip)
        except:
            pass
        
        # Try to get all interface IPs (fallback method)
        try:
            hostname = socket.gethostname()
            all_ips = socket.gethostbyname_ex(hostname)[2]
            for ip in all_ips:
                if not ip.startswith("127.") and ip not in ips:
                    ips.append(ip)
        except:
            pass
            
        return ips
    
    print("Starting IoT Command Server...")
    
    local_ips = get_local_ips()
    print("Server will be available on:")
    for ip in local_ips:
        print(f"  Web interface: http://{ip}:5000")
        print(f"  Device command endpoint: http://{ip}:5000/command")
        print(f"  Device response endpoint: http://{ip}:5000/response")
        print()
    
    if '192.168.0.101' not in local_ips:
        print("Note: 192.168.0.101 is not detected as a local IP address.")
        print("If this IP exists on your system, the server will still be accessible at:")
        print("  http://192.168.0.101:5000")
        print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)