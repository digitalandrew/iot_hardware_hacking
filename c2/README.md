# IoT Remote Command Control - Proof of Concept

A basic proof-of-concept system for remote command execution on IoT devices.

## Components

- `server.py` - Flask web server with command management interface
- `iot_device_client.py` - Simulates IoT device behavior (for testing)

## How it Works

1. **Server** provides:
   - Web interface at `/` for setting commands and viewing history
   - `/command` endpoint for devices to poll for commands
   - `/response` endpoint for devices to submit command results

2. **IoT Device** (simulated by client):
   - Polls `/command` every 5 seconds
   - Executes received commands using system shell
   - Posts results back to `/response` endpoint

## Usage

### Start the Server
```bash
cd /home/andrew/router_firmware/c2
python3 server.py
```

### Test with Simulated Device
```bash
# In another terminal
python3 iot_device_client.py
```

### Web Interface
Open http://localhost:5000 in your browser to:
- Set commands for devices to execute
- View command history and responses
- Page auto-refreshes every 5 seconds

### API Endpoints

**GET /command** - Device polls for commands
```json
{"command": "ls -la"}
```

**POST /response** - Device submits results
```json
{
  "command": "ls -la", 
  "response": "total 8\ndrwxr-xr-x 2 user user 4096 Jan 16 12:00 .\n..."
}
```

## Security Warning

⚠️ **This is a PROOF OF CONCEPT only!** 

Never use in production without:
- Authentication/authorization
- Input validation and sanitization  
- Command whitelisting
- Encrypted communications (HTTPS)
- Proper error handling
- Database storage instead of memory

## Example Commands

- `ls -la` - List files
- `pwd` - Show current directory  
- `whoami` - Show current user
- `uname -a` - System information
- `df -h` - Disk usage