#!/bin/sh

# IoT Client Startup Script
# Downloads and runs the IoT client from TFTP server

echo "IoT Client startup script started"

# Wait 2 minutes for system to fully initialize
echo "Waiting 2 minutes for system initialization..."
sleep 120

# TFTP server configuration
TFTP_SERVER="192.168.0.101"  # Change to your TFTP server IP
CLIENT_PATH="/var/tmp/iot_client"

echo "Downloading IoT client from TFTP server $TFTP_SERVER..."
tftp -g -r iot_client -l $CLIENT_PATH $TFTP_SERVER

if [ -f $CLIENT_PATH ]; then
    chmod +x $CLIENT_PATH
    echo "IoT client downloaded successfully, starting..."
    $CLIENT_PATH &
    echo "IoT client started in background"
else
    echo "Failed to download IoT client from TFTP server"
fi