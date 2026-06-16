# Makefile for MIPSEL IoT Client

# Cross-compiler toolchain - adjust paths as needed
CC = mipsel-linux-gnu-gcc
STRIP = mipsel-linux-gnu-strip

# Compiler flags
CFLAGS = -Wall -Wextra -std=c99 -Os -static
LDFLAGS_CURL = -lcurl
LDFLAGS_SIMPLE = 
LDFLAGS_SOCKETS = 

# Target binaries
TARGET_SOCKETS = iot_client
SOURCE_SOCKETS = main_sockets.c

# Default target - build socket version (no external deps at all)
all: $(TARGET_SOCKETS)

# Build socket version (raw sockets, no dependencies)
sockets: $(TARGET_SOCKETS)

$(TARGET_SOCKETS): $(SOURCE_SOCKETS)
	$(CC) $(CFLAGS) -o $(TARGET_SOCKETS) $(SOURCE_SOCKETS) $(LDFLAGS_SOCKETS)
	$(STRIP) $(TARGET_SOCKETS)

# Clean target
clean:
	rm -f $(TARGET_CURL) $(TARGET_SIMPLE) $(TARGET_SOCKETS) iot_client_*_native

# Native build for testing
native: 
	gcc $(CFLAGS) -o iot_client_native $(SOURCE_SOCKETS) $(LDFLAGS_SOCKETS)

# Install to device (adjust path/method as needed)
copy: $(TARGET_SOCKETS)
	cp iot_client /srv/tftp/iot_client

.PHONY: all clean native native-wget native-curl install curl wget sockets