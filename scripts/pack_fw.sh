#!/bin/sh

# Check if base firmware exists
if [ ! -f "../original_fw.bin" ]; then
    echo "Error: original_fw.bin not found. Please provide the base firmware file."
    exit 1
fi

# Remove old squashfs file to avoid appending
rm -f rfs.squashfs

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
