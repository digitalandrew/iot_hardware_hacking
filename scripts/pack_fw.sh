#!/bin/sh

# Check if base firmware exists
if [ ! -f "../original_fw.bin" ]; then
    echo "Error: original_fw.bin not found. Please provide the base firmware file."
    exit 1
fi

# Remove old squashfs file to avoid appending
rm -f rfs.squashfs

# Create essential device nodes if they don't exist
DEV_DIR="../patch_rfs/dev"
if [ ! -c "$DEV_DIR/null" ]; then
    echo "Creating essential device nodes..."
    sudo mknod "$DEV_DIR/null" c 1 3 && sudo chmod 666 "$DEV_DIR/null"
    sudo mknod "$DEV_DIR/console" c 5 1 && sudo chmod 620 "$DEV_DIR/console"
    sudo mknod "$DEV_DIR/zero" c 1 5 && sudo chmod 666 "$DEV_DIR/zero"
    sudo mknod "$DEV_DIR/random" c 1 8 && sudo chmod 666 "$DEV_DIR/random"
    sudo mknod "$DEV_DIR/urandom" c 1 9 && sudo chmod 666 "$DEV_DIR/urandom"
    sudo mknod "$DEV_DIR/ttyS0" c 4 64 && sudo chmod 660 "$DEV_DIR/ttyS0"
    sudo mknod "$DEV_DIR/ttyS1" c 4 65 && sudo chmod 660 "$DEV_DIR/ttyS1"
    echo "Device nodes created."
fi

#create squashfs file system with original firmware settings and proper ownership
mksquashfs ../patch_rfs/ rfs.squashfs -comp xz -b 262144 -always-use-fragments -all-root

# Check squashfs size against rootfs partition (allowing some extra room)
SQUASHFS_SIZE=$(stat -c%s rfs.squashfs)
MAX_ROOTFS_SIZE=3200000  # ~3.2MB instead of 2.94MB to allow for growth
if [ $SQUASHFS_SIZE -gt $MAX_ROOTFS_SIZE ]; then
    echo "Error: squashfs size ($SQUASHFS_SIZE) exceeds maximum allowed size ($MAX_ROOTFS_SIZE)"
    exit 1
fi

# Copy base firmware
cp ../original_fw.bin patch_fw.bin

#patch firmware with new rfs (rootfs starts at 0x100000)
dd if=rfs.squashfs of=patch_fw.bin conv=notrunc bs=1 seek=1048576

echo "Firmware patched successfully. Squashfs size: $SQUASHFS_SIZE bytes"
