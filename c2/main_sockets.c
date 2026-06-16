#define _GNU_SOURCE  // For popen/pclose

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/wait.h>
#include <errno.h>

#define SERVER_IP "192.168.0.101"  // Change to your server IP
#define SERVER_PORT 5000
#define POLL_INTERVAL 5  // seconds
#define MAX_COMMAND_SIZE 512
#define MAX_RESPONSE_SIZE 2048
#define HTTP_TIMEOUT 10

// Execute a system command and capture output
char* execute_command(const char* command) {
    FILE *fp;
    char *result = malloc(MAX_RESPONSE_SIZE);
    char buffer[256];
    
    if (!result) {
        return NULL;
    }
    
    result[0] = '\0';  // Initialize empty string
    
    // Execute command and capture output
    fp = popen(command, "r");
    if (fp == NULL) {
        snprintf(result, MAX_RESPONSE_SIZE, "Error: Failed to execute command");
        return result;
    }
    
    // Read command output
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        if (strlen(result) + strlen(buffer) < MAX_RESPONSE_SIZE - 1) {
            strcat(result, buffer);
        }
    }
    
    int status = pclose(fp);
    
    // If no output, add status message
    if (strlen(result) == 0) {
        snprintf(result, MAX_RESPONSE_SIZE, "Command completed (exit code: %d)", WEXITSTATUS(status));
    }
    
    return result;
}

// Create socket connection to server
int connect_to_server() {
    int sock;
    struct sockaddr_in server_addr;
    
    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        printf("[IoT Client] ERROR: Cannot create socket: %s\n", strerror(errno));
        return -1;
    }
    
    // Set socket timeout
    struct timeval timeout;
    timeout.tv_sec = HTTP_TIMEOUT;
    timeout.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        printf("[IoT Client] ERROR: Invalid server IP address: %s\n", SERVER_IP);
        close(sock);
        return -1;
    }
    
    // Connect to server
    printf("[IoT Client] Connecting to %s:%d...\n", SERVER_IP, SERVER_PORT);
    fflush(stdout);
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        printf("[IoT Client] ERROR: Cannot connect to server: %s\n", strerror(errno));
        close(sock);
        return -1;
    }
    printf("[IoT Client] Connected successfully\n");
    fflush(stdout);
    
    return sock;
}

// Make HTTP GET request
char* http_get(const char* path) {
    int sock;
    char request[512];
    char *response = NULL;
    char buffer[1024];
    int bytes_received;
    int total_size = 0;
    
    sock = connect_to_server();
    if (sock < 0) {
        return NULL;
    }
    
    // Build HTTP GET request
    snprintf(request, sizeof(request),
             "GET %s HTTP/1.1\r\n"
             "Host: %s:%d\r\n"
             "Connection: close\r\n"
             "User-Agent: IoTDevice/1.0\r\n"
             "\r\n",
             path, SERVER_IP, SERVER_PORT);
    
    // Send request
    printf("[IoT Client] Sending GET request to %s\n", path);
    fflush(stdout);
    if (send(sock, request, strlen(request), 0) < 0) {
        printf("[IoT Client] ERROR: Cannot send request: %s\n", strerror(errno));
        close(sock);
        return NULL;
    }
    printf("[IoT Client] Request sent, waiting for response...\n");
    fflush(stdout);
    
    // Receive response
    response = malloc(MAX_RESPONSE_SIZE);
    if (!response) {
        close(sock);
        return NULL;
    }
    
    response[0] = '\0';
    
    while ((bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
        buffer[bytes_received] = '\0';
        
        if (total_size + bytes_received < MAX_RESPONSE_SIZE - 1) {
            strcat(response, buffer);
            total_size += bytes_received;
        } else {
            break;
        }
    }
    
    close(sock);
    
    // Find start of JSON (after HTTP headers)
    char *json_start = strstr(response, "\r\n\r\n");
    if (json_start) {
        json_start += 4; // Skip the \r\n\r\n
        memmove(response, json_start, strlen(json_start) + 1);
    }
    
    return response;
}

// Make HTTP POST request
int http_post(const char* path, const char* data) {
    int sock;
    char request[4096];
    char buffer[512];
    int success = 0;
    
    sock = connect_to_server();
    if (sock < 0) {
        return 0;
    }
    
    // Build HTTP POST request
    snprintf(request, sizeof(request),
             "POST %s HTTP/1.1\r\n"
             "Host: %s:%d\r\n"
             "Content-Type: application/json\r\n"
             "Content-Length: %u\r\n"
             "Connection: close\r\n"
             "User-Agent: IoTDevice/1.0\r\n"
             "\r\n"
             "%s",
             path, SERVER_IP, SERVER_PORT, (unsigned int)strlen(data), data);
    
    // Send request
    printf("[IoT Client] Sending POST request to %s\n", path);
    fflush(stdout);
    if (send(sock, request, strlen(request), 0) >= 0) {
        printf("[IoT Client] POST data sent, checking response...\n");
        fflush(stdout);
        // Read response to check status
        int bytes = recv(sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            printf("[IoT Client] Received HTTP response: %.50s...\n", buffer);
            fflush(stdout);
            // Check for HTTP 200 OK
            if (strstr(buffer, "HTTP/1.1 200") || strstr(buffer, "HTTP/1.0 200")) {
                success = 1;
                printf("[IoT Client] HTTP 200 OK received\n");
            } else {
                printf("[IoT Client] HTTP error response received\n");
            }
        } else {
            printf("[IoT Client] No response received from server\n");
        }
    } else {
        printf("[IoT Client] ERROR: Failed to send POST request: %s\n", strerror(errno));
    }
    
    close(sock);
    return success;
}

// Poll server for command
char* poll_command() {
    char *response = http_get("/command");
    char *command = NULL;
    
    if (response) {
        printf("[IoT Client] Raw response: %s\n", response);
        fflush(stdout);
        
        // Simple JSON parsing - look for "command":"value"
        char *cmd_start = strstr(response, "\"command\":");
        if (cmd_start) {
            // Move past "command":
            cmd_start += 10; // length of "command":
            
            // Skip any whitespace
            while (*cmd_start == ' ' || *cmd_start == '\t') {
                cmd_start++;
            }
            
            // Should now be at the opening quote of the value
            if (*cmd_start == '"') {
                cmd_start++; // Move past opening quote
                char *cmd_end = strchr(cmd_start, '"');  // Find closing quote
                if (cmd_end && cmd_end > cmd_start) {
                    int len = cmd_end - cmd_start;
                    command = malloc(len + 1);
                    if (command) {
                        strncpy(command, cmd_start, len);
                        command[len] = '\0';
                        printf("[IoT Client] Parsed command: '%s'\n", command);
                        fflush(stdout);
                    }
                } else if (cmd_end == cmd_start) {
                    // Empty command
                    command = malloc(1);
                    if (command) {
                        command[0] = '\0';
                        printf("[IoT Client] Parsed empty command\n");
                        fflush(stdout);
                    }
                }
            }
        }
        free(response);
    }
    
    return command;
}

// Submit response to server
int submit_response(const char* command, const char* response) {
    char *json_data;
    int success = 0;
    
    // Allocate memory for JSON
    json_data = malloc(MAX_RESPONSE_SIZE + MAX_COMMAND_SIZE + 100);
    if (!json_data) {
        return 0;
    }
    
    // Build JSON with basic escaping
    strcpy(json_data, "{\"command\":\"");
    
    // Escape command
    char *pos = json_data + strlen(json_data);
    for (const char *p = command; *p; p++) {
        if (*p == '"' || *p == '\\') *pos++ = '\\';
        *pos++ = *p;
    }
    *pos = '\0';
    
    strcat(json_data, "\",\"response\":\"");
    
    // Escape response
    pos = json_data + strlen(json_data);
    for (const char *p = response; *p; p++) {
        if (*p == '"' || *p == '\\') {
            *pos++ = '\\';
            *pos++ = *p;
        } else if (*p == '\n') {
            *pos++ = '\\';
            *pos++ = 'n';
        } else if (*p == '\r') {
            *pos++ = '\\';
            *pos++ = 'r';
        } else if (*p == '\t') {
            *pos++ = '\\';
            *pos++ = 't';
        } else {
            *pos++ = *p;
        }
    }
    *pos = '\0';
    
    strcat(json_data, "\"}");
    
    // Send POST request
    success = http_post("/response", json_data);
    
    free(json_data);
    return success;
}

int main() {
    printf("[IoT Client] Starting up (raw sockets implementation)\n");
    printf("[IoT Client] Server: %s:%d\n", SERVER_IP, SERVER_PORT);
    printf("[IoT Client] Poll interval: %d seconds\n", POLL_INTERVAL);
    printf("[IoT Client] Ready - polling for commands...\n");
    fflush(stdout);
    
    char last_command[MAX_COMMAND_SIZE] = "";
    int poll_count = 0;
    
    while (1) {
        poll_count++;
        printf("[IoT Client] Poll #%d - checking for new commands...\n", poll_count);
        fflush(stdout);
        
        // Poll for command
        char *command = poll_command();
        
        if (command && strlen(command) > 0) {
            if (strcmp(command, last_command) != 0) {
                printf("[IoT Client] NEW COMMAND received: '%s'\n", command);
                printf("[IoT Client] Executing command...\n");
                fflush(stdout);
                
                // Execute command
                char *response = execute_command(command);
                if (response) {
                    printf("[IoT Client] Command completed. Response length: %u bytes\n", (unsigned int)strlen(response));
                    printf("[IoT Client] Response: %s\n", response);
                    printf("[IoT Client] Submitting response to server...\n");
                    fflush(stdout);
                    
                    // Submit response
                    if (submit_response(command, response)) {
                        printf("[IoT Client] Response submitted successfully\n");
                    } else {
                        printf("[IoT Client] ERROR: Failed to submit response\n");
                    }
                    
                    free(response);
                } else {
                    printf("[IoT Client] ERROR: Failed to execute command\n");
                }
                
                // Update last command
                strncpy(last_command, command, MAX_COMMAND_SIZE - 1);
                last_command[MAX_COMMAND_SIZE - 1] = '\0';
            } else {
                printf("[IoT Client] Same command as before - skipping\n");
            }
        } else {
            printf("[IoT Client] No command received or empty command\n");
        }
        
        if (command) {
            free(command);
        }
        
        printf("[IoT Client] Sleeping for %d seconds...\n", POLL_INTERVAL);
        fflush(stdout);
        sleep(POLL_INTERVAL);
    }
    
    return 0;
}