#!/usr/bin/env python3
"""
Android Bootanimation & Rootless Flashable ZIP Generator
Convert any GIF into an Android bootanimation for any phone resolution
and produce flashable recovery ZIPs with automated backup.
"""

import argparse
import glob
import hashlib
import io
import math
import os
import shutil
import sys
import tempfile
import time
import zipfile
from typing import List, Tuple, Optional, Dict

try:
    from PIL import Image, ImageSequence
except ImportError:
    print("\033[91mError: Pillow (PIL) is not installed.\033[0m")
    print("Please install it with: pip install Pillow")
    sys.exit(1)

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

BANNER = f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║         Android Bootanimation & Flashable ZIP Creator         ║
║          Convert GIFs -> Rootless Flashable Recovery ZIPs     ║
║             With Automatic Device Backup & Restore            ║
╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""

# Predefined Phone Models & Codenames Database
DEVICE_PRESETS = {
    # Xiaomi / Redmi / POCO
    "begonia": {
        "name": "Redmi Note 8 Pro",
        "brand": "Xiaomi / Redmi",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["redmi note 8 pro", "rn8p", "begoniain", "redmi-note-8-pro", "bego"]
    },
    "ginkgo": {
        "name": "Redmi Note 8",
        "brand": "Xiaomi / Redmi",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["redmi note 8", "rn8", "redmi-note-8"]
    },
    "sweet": {
        "name": "Redmi Note 10 Pro",
        "brand": "Xiaomi / Redmi",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["redmi note 10 pro", "rn10p", "sweetin"]
    },
    "vayu": {
        "name": "POCO X3 Pro",
        "brand": "POCO",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["poco x3 pro", "bhima", "pocox3pro"]
    },
    "alioth": {
        "name": "POCO F3 / Redmi K40",
        "brand": "POCO / Redmi",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["poco f3", "redmi k40", "pocof3"]
    },
    "marble": {
        "name": "POCO F5 / Redmi Note 12 Turbo",
        "brand": "POCO / Redmi",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["poco f5", "redmi note 12 turbo", "pocof5"]
    },
    "peridot": {
        "name": "POCO F6 / Redmi Turbo 3",
        "brand": "POCO / Redmi",
        "resolution": (1220, 2712),
        "fps": 30,
        "aliases": ["poco f6", "redmi turbo 3", "pocof6"]
    },
    "beryllium": {
        "name": "POCO F1",
        "brand": "POCO",
        "resolution": (1080, 2246),
        "fps": 30,
        "aliases": ["poco f1", "pocophone f1", "pocof1"]
    },
    "whyred": {
        "name": "Redmi Note 5 Pro",
        "brand": "Xiaomi / Redmi",
        "resolution": (1080, 2160),
        "fps": 30,
        "aliases": ["redmi note 5 pro", "rn5p"]
    },
    "surya": {
        "name": "POCO X3 / X3 NFC",
        "brand": "POCO",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["poco x3", "poco x3 nfc", "karna"]
    },

    # Google Pixel
    "husky": {
        "name": "Google Pixel 8 Pro",
        "brand": "Google",
        "resolution": (1344, 2992),
        "fps": 30,
        "aliases": ["pixel 8 pro", "pixel8pro", "pixel-8-pro"]
    },
    "shiba": {
        "name": "Google Pixel 8",
        "brand": "Google",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["pixel 8", "pixel8", "pixel-8"]
    },
    "cheetah": {
        "name": "Google Pixel 7 Pro",
        "brand": "Google",
        "resolution": (1440, 3120),
        "fps": 30,
        "aliases": ["pixel 7 pro", "pixel7pro", "pixel-7-pro"]
    },
    "panther": {
        "name": "Google Pixel 7",
        "brand": "Google",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["pixel 7", "pixel7", "pixel-7"]
    },
    "raven": {
        "name": "Google Pixel 6 Pro",
        "brand": "Google",
        "resolution": (1440, 3120),
        "fps": 30,
        "aliases": ["pixel 6 pro", "pixel6pro"]
    },
    "oriole": {
        "name": "Google Pixel 6",
        "brand": "Google",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["pixel 6", "pixel6"]
    },
    "redfin": {
        "name": "Google Pixel 5",
        "brand": "Google",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["pixel 5", "pixel5"]
    },
    "sunfish": {
        "name": "Google Pixel 4a",
        "brand": "Google",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["pixel 4a", "pixel4a"]
    },

    # Samsung Galaxy
    "s24u": {
        "name": "Samsung Galaxy S24 Ultra",
        "brand": "Samsung",
        "resolution": (1440, 3120),
        "fps": 30,
        "aliases": ["galaxy s24 ultra", "s24 ultra", "s24u", "e3s"]
    },
    "s24": {
        "name": "Samsung Galaxy S24 / S24+",
        "brand": "Samsung",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["galaxy s24", "galaxy s24+", "s24", "e1s", "e2s"]
    },
    "s23u": {
        "name": "Samsung Galaxy S23 Ultra",
        "brand": "Samsung",
        "resolution": (1440, 3088),
        "fps": 30,
        "aliases": ["galaxy s23 ultra", "s23 ultra", "s23u"]
    },
    "s23": {
        "name": "Samsung Galaxy S23",
        "brand": "Samsung",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["galaxy s23", "s23"]
    },
    "s22u": {
        "name": "Samsung Galaxy S22 Ultra",
        "brand": "Samsung",
        "resolution": (1440, 3088),
        "fps": 30,
        "aliases": ["galaxy s22 ultra", "s22 ultra", "s22u"]
    },
    "s21": {
        "name": "Samsung Galaxy S21 / S20",
        "brand": "Samsung",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["galaxy s21", "galaxy s20", "s21", "s20"]
    },
    "a54": {
        "name": "Samsung Galaxy A54 / A55",
        "brand": "Samsung",
        "resolution": (1080, 2340),
        "fps": 30,
        "aliases": ["galaxy a54", "galaxy a55", "a54", "a55"]
    },
    "a52": {
        "name": "Samsung Galaxy A52 / A53",
        "brand": "Samsung",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["galaxy a52", "galaxy a53", "a52", "a53"]
    },

    # OnePlus / Nothing
    "guacamole": {
        "name": "OnePlus 7 Pro",
        "brand": "OnePlus",
        "resolution": (1440, 3120),
        "fps": 30,
        "aliases": ["oneplus 7 pro", "op7p", "oneplus7pro"]
    },
    "instantnoodle": {
        "name": "OnePlus 8",
        "brand": "OnePlus",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["oneplus 8", "op8", "oneplus8"]
    },
    "spacewar": {
        "name": "Nothing Phone (1)",
        "brand": "Nothing",
        "resolution": (1080, 2400),
        "fps": 30,
        "aliases": ["nothing phone 1", "nothing phone (1)", "np1"]
    },
    "pong": {
        "name": "Nothing Phone (2)",
        "brand": "Nothing",
        "resolution": (1080, 2412),
        "fps": 30,
        "aliases": ["nothing phone 2", "nothing phone (2)", "np2"]
    },
}

def lookup_phone(query: str) -> Optional[Tuple[str, dict]]:
    """Look up a phone by codename or alias (case-insensitive)."""
    q = query.strip().lower()
    # Exact codename match
    if q in DEVICE_PRESETS:
        return (q, DEVICE_PRESETS[q])
    
    # Check aliases and names
    for codename, data in DEVICE_PRESETS.items():
        if q == data["name"].lower():
            return (codename, data)
        for alias in data.get("aliases", []):
            if q == alias.lower():
                return (codename, data)
    
    # Partial substring match
    for codename, data in DEVICE_PRESETS.items():
        if q in codename or q in data["name"].lower():
            return (codename, data)
        for alias in data.get("aliases", []):
            if q in alias.lower():
                return (codename, data)
    return None

def list_predefined_phones():
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Predefined Phone Models & Codenames ==={Colors.RESET}\n")
    print(f"{'Codename':<16} {'Model Name':<34} {'Resolution':<14} {'FPS':<6}")
    print("-" * 74)
    for codename, data in DEVICE_PRESETS.items():
        res_str = f"{data['resolution'][0]}x{data['resolution'][1]}"
        star = " ★ [YOUR PHONE]" if codename == "begonia" else ""
        print(f"{Colors.BOLD}{codename:<16}{Colors.RESET} {data['name'] + star:<34} {res_str:<14} {data['fps']} FPS")
    print(f"\nTip: Run with {Colors.BOLD}-p <codename>{Colors.RESET} (e.g. {Colors.GREEN}{Colors.BOLD}python3 main.py -i gifs/BLYkag.gif -p begonia{Colors.RESET})\n")

# Common Android Display Presets (Width x Height)
PRESETS = {
    "1": ("1080x2340", "begonia (Redmi Note 8 Pro) / Galaxy S23/S24 [1080x2340 19.5:9]"),
    "2": ("1080x2400", "FHD+ 20:9 (Pixel 6/7/8, POCO X3/F3/F5, Nothing, OnePlus)"),
    "3": ("1440x3120", "QHD+ 19.5:9 (Pixel 6/7/8 Pro, Galaxy S24 Ultra, OnePlus 7 Pro)"),
    "4": ("1440x3200", "QHD+ 20:9 (Galaxy S20/S21 Ultra, Xiaomi Ultra)"),
    "5": ("1080x1920", "FHD 16:9 (Standard / Classic Android Phones)"),
    "6": ("720x1600",  "HD+ 20:9 (Entry-level / Budget Android Phones)"),
    "7": ("1220x2712", "1.5K (POCO F6 / Redmi Turbo 3 / Xiaomi 13T)"),
    "8": ("original",  "Original GIF dimensions"),
    "9": ("custom",    "Custom Width x Height (e.g. 1080x2400)")
}

# --- POSIX UPDATE-BINARY SHELL SCRIPT GENERATORS ---

def get_update_binary_installer(device_name: str = "", device_codename: str = "") -> str:
    device_line = ""
    if device_name and device_codename:
        label = f"{device_name} ({device_codename})"
        device_line = f'ui_print " Target Device: {label}"\n'
    elif device_name or device_codename:
        label = device_name or device_codename
        device_line = f'ui_print " Target Device: {label}"\n'

    return f"""#!/sbin/sh
# ==========================================================
# Universal Rootless Bootanimation Installer
# Features:
#   - 100% Rootless: Runs directly in TWRP/OrangeFox/PBRP/etc.
#   - Automatic Partition Mounting (SAR, Dynamic, Legacy)
#   - Automatic Location Detection across Android versions
#   - In-place Backup (.bak) + Internal Storage Backup
#   - Generates On-Device Restore Script
# ==========================================================

OUTFD=$2
ZIPFILE=$3

# Find file descriptor for TWRP ui_print
if [ -z "$OUTFD" ] || [ ! -e "/proc/self/fd/$OUTFD" ]; then
    OUTFD=1
fi

ui_print() {{
    if [ "$OUTFD" != "1" ] && [ -e "/proc/self/fd/$OUTFD" ]; then
        echo "ui_print $1" > "/proc/self/fd/$OUTFD"
        echo "ui_print " > "/proc/self/fd/$OUTFD"
    else
        echo "$1"
    fi
}}

set_progress() {{
    if [ "$OUTFD" != "1" ] && [ -e "/proc/self/fd/$OUTFD" ]; then
        echo "set_progress $1" > "/proc/self/fd/$OUTFD"
    fi
}}

ui_print "==========================================="
ui_print " Universal Bootanimation Installer"
ui_print " Rootless Recovery Flashable with Auto-Backup"
{device_line}ui_print "==========================================="

set_progress 0.1

# 1. Mount Partitions
ui_print "- Mounting partitions..."

mount_partition() {{
    local part="$1"
    local mnt="$2"

    if grep -q " $mnt " /proc/mounts 2>/dev/null; then
        mount -o rw,remount "$mnt" 2>/dev/null || mount -o remount,rw "$mnt" 2>/dev/null
        return 0
    fi

    mkdir -p "$mnt" 2>/dev/null
    mount -o rw "$mnt" 2>/dev/null && return 0
    mount "$mnt" 2>/dev/null && mount -o rw,remount "$mnt" 2>/dev/null && return 0

    for dev in /dev/block/bootdevice/by-name/"$part" /dev/block/by-name/"$part" /dev/block/mapper/"$part"; do
        if [ -b "$dev" ]; then
            mount -o rw "$dev" "$mnt" 2>/dev/null && return 0
            mount "$dev" "$mnt" 2>/dev/null && mount -o rw,remount "$mnt" 2>/dev/null && return 0
        fi
    done
    return 1
}}

mount_partition system /system
mount_partition system_root /system_root
mount_partition product /product
mount_partition system_ext /system_ext
mount_partition vendor /vendor
mount_partition data /data
mount_partition userdata /data

# Try remounting everything rw
mount -o rw,remount /system 2>/dev/null
mount -o rw,remount /system_root 2>/dev/null
mount -o rw,remount /system_root/system 2>/dev/null
mount -o rw,remount /product 2>/dev/null
mount -o rw,remount /system_ext 2>/dev/null

set_progress 0.3

# 2. Locate Active Bootanimation
ui_print "- Detecting bootanimation location..."

CANDIDATES="
/product/media/bootanimation.zip
/system/product/media/bootanimation.zip
/system_root/product/media/bootanimation.zip
/system_root/system/product/media/bootanimation.zip
/system_ext/media/bootanimation.zip
/system/system_ext/media/bootanimation.zip
/system_root/system_ext/media/bootanimation.zip
/system/media/bootanimation.zip
/system_root/system/media/bootanimation.zip
/system_root/media/bootanimation.zip
/oem/media/bootanimation.zip
/vendor/media/bootanimation.zip
"

TARGET=""
FOUND_EXISTING=0

for path in $CANDIDATES; do
    if [ -f "$path" ]; then
        TARGET="$path"
        FOUND_EXISTING=1
        break
    fi
done

# If not found existing, pick most suitable path based on mounted directory
if [ -z "$TARGET" ]; then
    if [ -d "/product/media" ]; then
        TARGET="/product/media/bootanimation.zip"
    elif [ -d "/system/product/media" ]; then
        TARGET="/system/product/media/bootanimation.zip"
    elif [ -d "/system/media" ]; then
        TARGET="/system/media/bootanimation.zip"
    elif [ -d "/system_root/system/media" ]; then
        TARGET="/system_root/system/media/bootanimation.zip"
    else
        mkdir -p /product/media 2>/dev/null && TARGET="/product/media/bootanimation.zip"
        if [ -z "$TARGET" ]; then
            mkdir -p /system/media 2>/dev/null && TARGET="/system/media/bootanimation.zip"
        fi
    fi
fi

# Fallback to /data/local if system partitions are completely inaccessible/read-only
if [ -z "$TARGET" ]; then
    mkdir -p /data/local 2>/dev/null
    TARGET="/data/local/bootanimation.zip"
fi

ui_print "  Target: $TARGET"

set_progress 0.5

# 3. Automatic Backup of Existing Bootanimation
BACKUP_STORAGE=""
for s in /sdcard /data/media/0 /storage/emulated/0; do
    if [ -d "$s" ] && [ -w "$s" ]; then
        BACKUP_STORAGE="$s"
        break
    fi
done

if [ "$FOUND_EXISTING" -eq 1 ]; then
    ui_print "- Backing up existing bootanimation..."
    
    # In-place backup
    cp -f "$TARGET" "${{TARGET}}.bak" 2>/dev/null
    if [ -f "${{TARGET}}.bak" ]; then
        ui_print "  In-place backup: ${{TARGET}}.bak"
    fi

    # Internal storage backup
    if [ -n "$BACKUP_STORAGE" ]; then
        BACKUP_DIR="$BACKUP_STORAGE/BootAnimation_Backups"
        mkdir -p "$BACKUP_DIR" 2>/dev/null
        
        TIMESTAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "timestamp")
        BACKUP_FILE="$BACKUP_DIR/bootanimation_backup_${{TIMESTAMP}}.zip"
        ORIGINAL_FILE="$BACKUP_DIR/bootanimation_original.zip"
        
        cp -f "$TARGET" "$BACKUP_FILE" 2>/dev/null
        if [ ! -f "$ORIGINAL_FILE" ]; then
            cp -f "$TARGET" "$ORIGINAL_FILE" 2>/dev/null
        fi

        # Save metadata info
        INFO_FILE="$BACKUP_DIR/backup_info.txt"
        echo "Original Target: $TARGET" > "$INFO_FILE"
        echo "Backup Date: $(date 2>/dev/null || echo 'Unknown')" >> "$INFO_FILE"
        echo "File Size: $(wc -c < "$TARGET" 2>/dev/null) bytes" >> "$INFO_FILE"
        echo "MD5: $(md5sum "$TARGET" 2>/dev/null | awk '{{print $1}}')" >> "$INFO_FILE"

        # Generate on-device restore shell script
        RESTORE_SH="$BACKUP_DIR/restore_bootanimation.sh"
        cat << 'EOF_RESTORE' > "$RESTORE_SH"
#!/sbin/sh
echo "Restoring original bootanimation..."
mount -o rw,remount /system 2>/dev/null
mount -o rw,remount /system_root 2>/dev/null
mount -o rw,remount /product 2>/dev/null
mount -o rw,remount /system_ext 2>/dev/null

TARGET_PATH="$(grep '^Original Target:' /sdcard/BootAnimation_Backups/backup_info.txt 2>/dev/null | cut -d' ' -f3)"
if [ -z "$TARGET_PATH" ]; then
    TARGET_PATH="/product/media/bootanimation.zip"
fi

if [ -f "/sdcard/BootAnimation_Backups/bootanimation_original.zip" ]; then
    cp -f "/sdcard/BootAnimation_Backups/bootanimation_original.zip" "$TARGET_PATH"
    chmod 644 "$TARGET_PATH"
    chown 0:0 "$TARGET_PATH" 2>/dev/null
    sync
    echo "Restored original bootanimation successfully to $TARGET_PATH"
else
    echo "Error: Backup file not found!"
fi
EOF_RESTORE
        chmod 755 "$RESTORE_SH" 2>/dev/null

        ui_print "  Saved backup to: $BACKUP_FILE"
        ui_print "  Saved info to:   $INFO_FILE"
        ui_print "  Created restore: $RESTORE_SH"
    fi
else
    ui_print "- No prior bootanimation detected. Fresh install."
fi

set_progress 0.7

# 4. Extract and Install New Bootanimation
ui_print "- Installing new bootanimation..."

NEW_ANIM="/tmp/bootanimation_extracted.zip"
rm -f "$NEW_ANIM" 2>/dev/null

# Resolve ZIPFILE path if not passed cleanly
if [ -z "$ZIPFILE" ] || [ ! -f "$ZIPFILE" ]; then
    for candidate in "$3" "$ZIP_FILE" /tmp/update.zip /sdcard/bootanimation_flashable_rootless*.zip; do
        if [ -f "$candidate" ]; then
            ZIPFILE="$candidate"
            break
        fi
    done
fi

ui_print "  Package: $ZIPFILE"

# Universal extraction (toybox & busybox compatible)
unzip -p "$ZIPFILE" bootanimation.zip > "$NEW_ANIM" 2>/dev/null
if [ ! -s "$NEW_ANIM" ]; then
    busybox unzip -p "$ZIPFILE" bootanimation.zip > "$NEW_ANIM" 2>/dev/null
fi
if [ ! -s "$NEW_ANIM" ]; then
    (cd /tmp && unzip -o "$ZIPFILE" bootanimation.zip >/dev/null 2>&1)
    [ -f "/tmp/bootanimation.zip" ] && mv -f /tmp/bootanimation.zip "$NEW_ANIM"
fi
if [ ! -s "$NEW_ANIM" ]; then
    (cd /tmp && busybox unzip -o "$ZIPFILE" bootanimation.zip >/dev/null 2>&1)
    [ -f "/tmp/bootanimation.zip" ] && mv -f /tmp/bootanimation.zip "$NEW_ANIM"
fi

if [ ! -s "$NEW_ANIM" ]; then
    ui_print "! Failed to extract bootanimation.zip from package: $ZIPFILE"
    exit 1
fi

TARGET_DIR=$(dirname "$TARGET")
mkdir -p "$TARGET_DIR" 2>/dev/null

# Try writing to target
cp -f "$NEW_ANIM" "$TARGET" 2>/dev/null
WRITE_SUCCESS=$?

# If failed due to read-only partition (EROFS / locked SAR), fallback to /data/local
if [ $WRITE_SUCCESS -ne 0 ] || [ ! -s "$TARGET" ]; then
    ui_print "! Notice: Target partition ($TARGET) is read-only (EROFS)."
    ui_print "  Falling back to writable /data/local/bootanimation.zip..."
    mkdir -p /data/local 2>/dev/null
    TARGET="/data/local/bootanimation.zip"
    cp -f "$NEW_ANIM" "$TARGET" 2>/dev/null
    if [ $? -ne 0 ] || [ ! -s "$TARGET" ]; then
        ui_print "! Error: Failed to copy bootanimation to $TARGET."
        exit 1
    fi
fi

# Set proper permissions and SELinux context
chmod 644 "$TARGET"
chown 0:0 "$TARGET" 2>/dev/null || chown root:root "$TARGET" 2>/dev/null
chcon u:object_r:system_file:s0 "$TARGET" 2>/dev/null || restorecon -v "$TARGET" 2>/dev/null

# If dark mode variant exists, sync it too if writable
DARK_TARGET="$(echo "$TARGET" | sed 's/bootanimation\\.zip/bootanimation-dark.zip/')"
if [ -f "$DARK_TARGET" ]; then
    cp -f "$TARGET" "$DARK_TARGET" 2>/dev/null
    chmod 644 "$DARK_TARGET" 2>/dev/null
    chown 0:0 "$DARK_TARGET" 2>/dev/null
fi

# Clean up
rm -rf "$TMP_EXTRACT" 2>/dev/null
sync

set_progress 1.0

ui_print "==========================================="
ui_print " Installation Successful!"
ui_print " Installed to: $TARGET"
if [ "$FOUND_EXISTING" -eq 1 ] && [ -n "$BACKUP_STORAGE" ]; then
    ui_print " Backup stored in: $BACKUP_STORAGE/BootAnimation_Backups"
    ui_print " Flash the restore zip anytime to revert."
fi
ui_print " Reboot and enjoy your new boot animation!"
ui_print "==========================================="

exit 0
"""

def get_update_binary_restorer(device_name: str = "", device_codename: str = "") -> str:
    device_line = ""
    if device_name and device_codename:
        label = f"{device_name} ({device_codename})"
        device_line = f'ui_print " Device: {label}"\n'
    elif device_name or device_codename:
        label = device_name or device_codename
        device_line = f'ui_print " Device: {label}"\n'

    return f"""#!/sbin/sh
# ==========================================================
# Universal Bootanimation Restore Package
# Automatically restores the backed-up stock bootanimation.
# ==========================================================

OUTFD=$2
if [ -z "$OUTFD" ] || [ ! -e "/proc/self/fd/$OUTFD" ]; then
    OUTFD=1
fi

ui_print() {{
    if [ "$OUTFD" != "1" ] && [ -e "/proc/self/fd/$OUTFD" ]; then
        echo "ui_print $1" > "/proc/self/fd/$OUTFD"
        echo "ui_print " > "/proc/self/fd/$OUTFD"
    else
        echo "$1"
    fi
}}

ui_print "==========================================="
ui_print " Bootanimation Restore Tool"
{device_line}ui_print "==========================================="

ui_print "- Mounting partitions..."
mount -o rw,remount /system 2>/dev/null
mount -o rw,remount /system_root 2>/dev/null
mount -o rw,remount /product 2>/dev/null
mount -o rw,remount /system_ext 2>/dev/null
mount -o rw /data 2>/dev/null

BACKUP_STORAGE=""
for s in /sdcard /data/media/0 /storage/emulated/0; do
    if [ -d "$s/BootAnimation_Backups" ]; then
        BACKUP_STORAGE="$s"
        break
    fi
done

TARGET=""
RESTORE_SOURCE=""

if [ -n "$BACKUP_STORAGE" ]; then
    INFO_FILE="$BACKUP_STORAGE/BootAnimation_Backups/backup_info.txt"
    if [ -f "$INFO_FILE" ]; then
        TARGET=$(grep '^Original Target:' "$INFO_FILE" | cut -d' ' -f3)
    fi
    
    ORIGINAL_FILE="$BACKUP_STORAGE/BootAnimation_Backups/bootanimation_original.zip"
    if [ -f "$ORIGINAL_FILE" ]; then
        RESTORE_SOURCE="$ORIGINAL_FILE"
    else
        # Find latest timestamped backup
        LATEST=$(ls -t "$BACKUP_STORAGE/BootAnimation_Backups"/bootanimation_backup_*.zip 2>/dev/null | head -n 1)
        if [ -n "$LATEST" ] && [ -f "$LATEST" ]; then
            RESTORE_SOURCE="$LATEST"
        fi
    fi
fi

# If target is still unknown, search for .bak file
if [ -z "$RESTORE_SOURCE" ] || [ -z "$TARGET" ]; then
    for bak in /product/media/bootanimation.zip.bak /system/media/bootanimation.zip.bak /system/product/media/bootanimation.zip.bak /data/local/bootanimation.zip.bak; do
        if [ -f "$bak" ]; then
            RESTORE_SOURCE="$bak"
            TARGET="${{bak%.bak}}"
            break
        fi
    done
fi

if [ -z "$RESTORE_SOURCE" ] || [ ! -f "$RESTORE_SOURCE" ]; then
    ui_print "! Error: No bootanimation backup found on device!"
    ui_print "  Checked /sdcard/BootAnimation_Backups and .bak files."
    exit 1
fi

if [ -z "$TARGET" ]; then
    TARGET="/product/media/bootanimation.zip"
fi

ui_print "- Restoring from: $RESTORE_SOURCE"
ui_print "- Restoring to:   $TARGET"

cp -f "$RESTORE_SOURCE" "$TARGET" 2>/dev/null
if [ $? -ne 0 ] || [ ! -s "$TARGET" ]; then
    # Try fallback to /data/local if system partition is locked
    ui_print "! Notice: Could not write to $TARGET, attempting /data/local..."
    TARGET="/data/local/bootanimation.zip"
    cp -f "$RESTORE_SOURCE" "$TARGET" 2>/dev/null
fi

if [ ! -s "$TARGET" ]; then
    ui_print "! Failed to restore bootanimation."
    exit 1
fi

chmod 644 "$TARGET"
chown 0:0 "$TARGET" 2>/dev/null || chown root:root "$TARGET" 2>/dev/null
chcon u:object_r:system_file:s0 "$TARGET" 2>/dev/null || restorecon -v "$TARGET" 2>/dev/null
sync

ui_print "==========================================="
ui_print " Original Bootanimation Restored!"
ui_print " Target: $TARGET"
ui_print "==========================================="
exit 0
"""

DUMMY_UPDATER_SCRIPT = "# Dummy updater-script for TWRP and custom recovery compatibility\n"

# --- MAGISK MODULE TEMPLATES ---

def get_magisk_module_prop(device_name: str = "", device_codename: str = "") -> str:
    desc_extra = f" for {device_name} ({device_codename})" if device_name else ""
    return f"""id=custom_bootanimation
name=Custom Bootanimation
version=v1.0
versionCode=1
author=BootAnimation Generator
description=Systemless custom bootanimation{desc_extra} generated from GIF.
"""

MAGISK_CUSTOMIZE_SH = """#!/sbin/sh
SKIPUNZIP=0

ui_print "- Installing Custom Bootanimation (Systemless Magisk Module)..."

# Ensure permissions
set_perm_recursive $MODPATH 0 0 0755 0644
set_perm $MODPATH/system/media/bootanimation.zip 0 0 0644
set_perm $MODPATH/system/product/media/bootanimation.zip 0 0 0644 2>/dev/null

ui_print "- Bootanimation successfully installed systemlessly!"
"""


# --- GIF PROCESSING & ANIMATION BUILDER ---

class BootAnimationBuilder:
    def __init__(
        self,
        gif_path: str,
        target_width: int,
        target_height: int,
        fps: Optional[int] = None,
        fit_mode: str = "contain",
        bg_color: str = "#000000",
        loop_mode: str = "infinite",
        pause_frames: int = 0
    ):
        self.gif_path = gif_path
        self.target_width = target_width
        self.target_height = target_height
        self.requested_fps = fps
        self.fit_mode = fit_mode.lower()
        self.bg_color = self._parse_color(bg_color)
        self.loop_mode = loop_mode
        self.pause_frames = pause_frames
        self.calculated_fps = 30
        self.frames: List[Image.Image] = []

    def _parse_color(self, hex_code: str) -> Tuple[int, int, int]:
        hex_clean = hex_code.strip().lstrip('#')
        if len(hex_clean) == 3:
            hex_clean = ''.join([c * 2 for c in hex_clean])
        if len(hex_clean) != 6:
            return (0, 0, 0)
        try:
            return (
                int(hex_clean[0:2], 16),
                int(hex_clean[2:4], 16),
                int(hex_clean[4:6], 16)
            )
        except ValueError:
            return (0, 0, 0)

    def extract_and_process_frames(self, progress_callback=None) -> int:
        """
        Extracts GIF frames handling disposal modes, transparency, timing,
        and resizes them to the target resolution using the selected fit mode.
        """
        if not os.path.isfile(self.gif_path):
            raise FileNotFoundError(f"GIF file not found: {self.gif_path}")

        img = Image.open(self.gif_path)
        durations = []
        raw_frames = []

        total_frames = getattr(img, 'n_frames', 1)

        # Iterate frames and handle GIF transparency & disposal methods
        last_frame_rgba = None
        for i in range(total_frames):
            img.seek(i)
            duration = img.info.get('duration', 70)
            if duration <= 10:  # Fix corrupted zero or near-zero durations
                duration = 70
            durations.append(duration)

            # Extract RGBA representation of current frame
            frame_rgba = img.convert('RGBA')

            # Handle disposal: if disposal is 2 (restore to background), previous is cleared
            disposal = img.info.get('disposal', 0)
            
            if last_frame_rgba is None or disposal == 2:
                canvas = Image.new('RGBA', img.size, (0, 0, 0, 0))
            else:
                canvas = last_frame_rgba.copy()

            canvas.paste(frame_rgba, (0, 0), frame_rgba)
            raw_frames.append(canvas.copy())

            if disposal != 2:
                last_frame_rgba = canvas

        # Calculate average FPS
        if durations:
            avg_duration_ms = sum(durations) / len(durations)
            native_fps = max(5, min(60, int(round(1000.0 / avg_duration_ms))))
        else:
            native_fps = 30

        self.calculated_fps = self.requested_fps if self.requested_fps and self.requested_fps > 0 else native_fps

        # Transform and scale each frame onto target screen canvas
        self.frames = []
        for idx, rf in enumerate(raw_frames):
            processed = self._transform_frame(rf)
            self.frames.append(processed)
            if progress_callback:
                progress_callback(idx + 1, total_frames)

        return len(self.frames)

    def _transform_frame(self, frame_rgba: Image.Image) -> Image.Image:
        """
        Resizes and positions a single RGBA frame onto a (target_width, target_height) canvas.
        Returns a 24-bit RGB Image.
        """
        orig_w, orig_h = frame_rgba.size
        dest_w, dest_h = self.target_width, self.target_height

        # Background canvas (RGB)
        canvas = Image.new('RGB', (dest_w, dest_h), self.bg_color)

        if self.fit_mode == "stretch":
            scaled = frame_rgba.resize((dest_w, dest_h), Image.Resampling.LANCZOS)
            canvas.paste(scaled, (0, 0), scaled)

        elif self.fit_mode == "cover":
            scale = max(dest_w / orig_w, dest_h / orig_h)
            new_w = int(round(orig_w * scale))
            new_h = int(round(orig_h * scale))
            scaled = frame_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Crop to center
            crop_x = (new_w - dest_w) // 2
            crop_y = (new_h - dest_h) // 2
            cropped = scaled.crop((crop_x, crop_y, crop_x + dest_w, crop_y + dest_h))
            canvas.paste(cropped, (0, 0), cropped)

        elif self.fit_mode == "center":
            # If image exceeds bounds, downscale to fit, else keep center
            if orig_w > dest_w or orig_h > dest_h:
                scale = min(dest_w / orig_w, dest_h / orig_h)
                new_w = int(round(orig_w * scale))
                new_h = int(round(orig_h * scale))
                scaled = frame_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                scaled = frame_rgba
                new_w, new_h = orig_w, orig_h
            pos_x = (dest_w - new_w) // 2
            pos_y = (dest_h - new_h) // 2
            canvas.paste(scaled, (pos_x, pos_y), scaled)

        else:  # "contain" or "fit" (Default)
            scale = min(dest_w / orig_w, dest_h / orig_h)
            new_w = int(round(orig_w * scale))
            new_h = int(round(orig_h * scale))
            scaled = frame_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
            pos_x = (dest_w - new_w) // 2
            pos_y = (dest_h - new_h) // 2
            canvas.paste(scaled, (pos_x, pos_y), scaled)

        return canvas

    def build_bootanimation_zip(self, output_path: str) -> str:
        """
        Creates Android bootanimation.zip with STORED compression (zero compression).
        CRITICAL: Android requires uncompressed ZIP format.
        """
        if not self.frames:
            raise ValueError("No frames available to build bootanimation.zip")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        loop_count = 0 if self.loop_mode == "infinite" else 1
        pause = self.pause_frames

        # Generate desc.txt
        # Format:
        # <width> <height> <fps>
        # p <count> <pause> <part_folder>
        desc_lines = [
            f"{self.target_width} {self.target_height} {self.calculated_fps}",
            f"p {loop_count} {pause} part0",
            ""  # Android desc.txt requires trailing newline
        ]
        desc_content = "\n".join(desc_lines).encode('utf-8')

        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_STORED) as zf:
            # 1. Write desc.txt
            zinfo_desc = zipfile.ZipInfo("desc.txt")
            zinfo_desc.external_attr = 0o644 << 16
            zf.writestr(zinfo_desc, desc_content)

            # 2. Write frames into part0/
            for idx, frame in enumerate(self.frames):
                frame_name = f"part0/{idx:05d}.png"
                img_buffer = io.BytesIO()
                frame.save(img_buffer, format='PNG', optimize=False)
                img_bytes = img_buffer.getvalue()

                zinfo_img = zipfile.ZipInfo(frame_name)
                zinfo_img.external_attr = 0o644 << 16
                zf.writestr(zinfo_img, img_bytes)

        return output_path

    @staticmethod
    def build_rootless_flashable_zip(
        bootanimation_zip_path: str,
        output_flashable_path: str,
        device_name: str = "",
        device_codename: str = ""
    ) -> str:
        """
        Builds a universal rootless recovery flashable ZIP containing update-binary,
        updater-script, and the bootanimation.zip.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_flashable_path)), exist_ok=True)

        installer_script = get_update_binary_installer(device_name, device_codename)

        with zipfile.ZipFile(output_flashable_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. Add update-binary (POSIX shell script for recovery)
            info_bin = zipfile.ZipInfo("META-INF/com/google/android/update-binary")
            info_bin.external_attr = 0o755 << 16  # Executable permissions
            zf.writestr(info_bin, installer_script)

            # 2. Add updater-script (dummy for compatibility)
            info_script = zipfile.ZipInfo("META-INF/com/google/android/updater-script")
            info_script.external_attr = 0o644 << 16
            zf.writestr(info_script, DUMMY_UPDATER_SCRIPT)

            # 3. Add bootanimation.zip (Uncompressed stored inside flashable package)
            info_boot = zipfile.ZipInfo("bootanimation.zip")
            info_boot.external_attr = 0o644 << 16
            with open(bootanimation_zip_path, 'rb') as f:
                zf.writestr(info_boot, f.read(), compress_type=zipfile.ZIP_STORED)

        return output_flashable_path

    @staticmethod
    def build_restore_flashable_zip(
        output_restore_path: str,
        device_name: str = "",
        device_codename: str = ""
    ) -> str:
        """
        Builds a standalone flashable ZIP that when flashed in TWRP restores the backed up animation.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_restore_path)), exist_ok=True)

        restorer_script = get_update_binary_restorer(device_name, device_codename)

        with zipfile.ZipFile(output_restore_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            info_bin = zipfile.ZipInfo("META-INF/com/google/android/update-binary")
            info_bin.external_attr = 0o755 << 16
            zf.writestr(info_bin, restorer_script)

            info_script = zipfile.ZipInfo("META-INF/com/google/android/updater-script")
            info_script.external_attr = 0o644 << 16
            zf.writestr(info_script, DUMMY_UPDATER_SCRIPT)

        return output_restore_path

    @staticmethod
    def build_magisk_module_zip(
        bootanimation_zip_path: str,
        output_magisk_path: str,
        device_name: str = "",
        device_codename: str = ""
    ) -> str:
        """
        Builds a systemless Magisk / KernelSU / APatch module ZIP.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_magisk_path)), exist_ok=True)

        with open(bootanimation_zip_path, 'rb') as f:
            boot_bytes = f.read()

        module_prop = get_magisk_module_prop(device_name, device_codename)

        with zipfile.ZipFile(output_magisk_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            # Module metadata
            zf.writestr("module.prop", module_prop)
            
            # Installation script
            info_cust = zipfile.ZipInfo("customize.sh")
            info_cust.external_attr = 0o755 << 16
            zf.writestr(info_cust, MAGISK_CUSTOMIZE_SH)

            # Recovery binary for flashing Magisk modules directly in TWRP
            info_bin = zipfile.ZipInfo("META-INF/com/google/android/update-binary")
            info_bin.external_attr = 0o755 << 16
            zf.writestr(info_bin, "#!/sbin/sh\nexec /data/adb/magisk/busybox sh $0 \"$@\"\n")

            zf.writestr("META-INF/com/google/android/updater-script", "#MAGISK\n")

            # Place bootanimation in standard system overlay paths
            info_sys = zipfile.ZipInfo("system/media/bootanimation.zip")
            info_sys.external_attr = 0o644 << 16
            zf.writestr(info_sys, boot_bytes, compress_type=zipfile.ZIP_STORED)

            info_prod = zipfile.ZipInfo("system/product/media/bootanimation.zip")
            info_prod.external_attr = 0o644 << 16
            zf.writestr(info_prod, boot_bytes, compress_type=zipfile.ZIP_STORED)

        return output_magisk_path


# --- CLI HELPERS & INTERACTIVE WIZARD ---

def print_progress(current: int, total: int, prefix: str = "Processing frames:"):
    percent = (current / total) * 100
    bar_len = 30
    filled = int(round(bar_len * current / float(total)))
    bar = '█' * filled + '░' * (bar_len - filled)
    sys.stdout.write(f"\r  {Colors.CYAN}{prefix}{Colors.RESET} [{bar}] {percent:.1f}% ({current}/{total})")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")


def find_local_gifs() -> List[str]:
    candidates = []
    candidates.extend(glob.glob("gifs/*.gif"))
    candidates.extend(glob.glob("*.gif"))
    candidates.extend(glob.glob("**/*.gif", recursive=True))
    unique = []
    for c in candidates:
        norm = os.path.normpath(c)
        if norm not in unique and not norm.startswith('.') and "output" not in norm:
            unique.append(norm)
    return sorted(unique)


def parse_resolution(res_str: str, gif_path: Optional[str] = None) -> Tuple[int, int]:
    res_str = res_str.strip().lower()
    if res_str == "original":
        if not gif_path or not os.path.isfile(gif_path):
            return (1080, 2400)
        with Image.open(gif_path) as im:
            return im.size
    
    if 'x' in res_str:
        parts = res_str.split('x')
        try:
            w = int(parts[0].strip())
            h = int(parts[1].strip())
            if w > 0 and h > 0:
                return (w, h)
        except ValueError:
            pass
    raise ValueError(f"Invalid resolution format: '{res_str}'. Expected WIDTHxHEIGHT (e.g. 1080x2400) or 'original'.")


def run_interactive_wizard():
    print(BANNER)
    print(f"{Colors.BOLD}{Colors.YELLOW}Interactive Setup Wizard{Colors.RESET}\n")

    # Step 1: Select GIF
    gifs = find_local_gifs()
    selected_gif = ""

    if gifs:
        print(f"{Colors.GREEN}Found GIF files in workspace:{Colors.RESET}")
        for idx, g in enumerate(gifs, 1):
            try:
                with Image.open(g) as im:
                    w, h = im.size
                    frames = getattr(im, 'n_frames', 1)
                    print(f"  [{idx}] {Colors.BOLD}{g}{Colors.RESET} ({w}x{h}, {frames} frames)")
            except Exception:
                print(f"  [{idx}] {g}")
        print(f"  [0] Enter custom path to a GIF file")

        choice = input(f"\n{Colors.BOLD}Select GIF [1-{len(gifs)}] (default 1): {Colors.RESET}").strip()
        if not choice:
            selected_gif = gifs[0]
        elif choice == "0":
            selected_gif = input("Enter path to GIF file: ").strip()
        else:
            try:
                c_idx = int(choice) - 1
                if 0 <= c_idx < len(gifs):
                    selected_gif = gifs[c_idx]
                else:
                    selected_gif = gifs[0]
            except ValueError:
                selected_gif = choice
    else:
        selected_gif = input("Enter path to GIF file: ").strip()

    while not os.path.isfile(selected_gif):
        print(f"{Colors.RED}File '{selected_gif}' does not exist!{Colors.RESET}")
        selected_gif = input("Enter path to valid GIF file: ").strip()

    # Step 2: Target Device / Resolution
    print(f"\n{Colors.GREEN}Select Target Phone / Resolution:{Colors.RESET}")
    print(f"  [b] {Colors.BOLD}{Colors.GREEN}begonia{Colors.RESET} - Redmi Note 8 Pro [1080x2340 19.5:9] ★ (Featured)")
    print(f"  [p] Choose from predefined phones (sweet, vayu, pixel8, s24, etc.)")
    for key, (res, desc) in PRESETS.items():
        print(f"  [{key}] {Colors.BOLD}{res.ljust(10)}{Colors.RESET} - {desc}")

    device_codename = None
    device_name = None
    target_fps = None

    dev_choice = input(f"\n{Colors.BOLD}Select device/preset (default 'b' for begonia): {Colors.RESET}").strip().lower()
    if not dev_choice or dev_choice in ['b', 'bego', 'begonia']:
        device_codename = "begonia"
        data = DEVICE_PRESETS["begonia"]
        device_name = data["name"]
        width, height = data["resolution"]
        target_fps = data["fps"]
    elif dev_choice == 'p':
        list_predefined_phones()
        phone_in = input(f"{Colors.BOLD}Enter phone codename or model: {Colors.RESET}").strip()
        found = lookup_phone(phone_in)
        if found:
            device_codename, data = found
            device_name = data["name"]
            width, height = data["resolution"]
            target_fps = data["fps"]
        else:
            print(f"{Colors.YELLOW}Unknown phone '{phone_in}'. Defaulting to 1080x2400.{Colors.RESET}")
            width, height = (1080, 2400)
    elif dev_choice == "9":  # Custom
        custom_res = input("Enter custom resolution (e.g. 1080x2400): ").strip()
        width, height = parse_resolution(custom_res)
    elif dev_choice == "8":  # Original
        width, height = parse_resolution("original", selected_gif)
    elif dev_choice in PRESETS:
        width, height = parse_resolution(PRESETS[dev_choice][0])
    else:
        # Check if user typed a codename directly
        found = lookup_phone(dev_choice)
        if found:
            device_codename, data = found
            device_name = data["name"]
            width, height = data["resolution"]
            target_fps = data["fps"]
        else:
            width, height = (1080, 2340)

    phone_label = f" ({device_name} / {device_codename})" if device_codename else ""
    print(f"  -> Target: {Colors.CYAN}{width}x{height}{phone_label}{Colors.RESET}")

    # Step 3: Fit Mode
    print(f"\n{Colors.GREEN}Select Display Fit Mode:{Colors.RESET}")
    print("  [1] contain / fit  - Keep aspect ratio, letterbox with background color (Recommended)")
    print("  [2] cover / crop   - Fill entire screen, crop excess borders")
    print("  [3] stretch        - Stretch to exact screen resolution")
    print("  [4] center         - Keep original size, center on screen")
    fit_choice = input(f"\n{Colors.BOLD}Select fit mode [1-4] (default 1): {Colors.RESET}").strip()
    fit_map = {"1": "contain", "2": "cover", "3": "stretch", "4": "center"}
    fit_mode = fit_map.get(fit_choice, "contain")

    # Step 4: Background Color
    bg_input = input(f"\n{Colors.BOLD}Background color hex (default #000000 black): {Colors.RESET}").strip()
    if not bg_input:
        bg_input = "#000000"

    # Step 5: FPS Override
    fps_prompt = f"Target FPS (default {target_fps if target_fps else 'auto'}): "
    fps_input = input(f"\n{Colors.BOLD}{fps_prompt}{Colors.RESET}").strip()
    if fps_input.isdigit() and int(fps_input) > 0:
        target_fps = int(fps_input)

    # Step 6: Output Directory
    out_dir_input = input(f"\n{Colors.BOLD}Output directory (default ./output): {Colors.RESET}").strip()
    output_dir = out_dir_input if out_dir_input else "./output"

    print(f"\n{Colors.YELLOW}Starting conversion...{Colors.RESET}")
    execute_conversion(
        gif_path=selected_gif,
        width=width,
        height=height,
        fps=target_fps,
        fit_mode=fit_mode,
        bg_color=bg_input,
        output_dir=output_dir,
        phone_codename=device_codename,
        phone_name=device_name,
        make_raw=True,
        make_flashable=True,
        make_restore=True,
        make_magisk=True
    )


def execute_conversion(
    gif_path: str,
    width: int,
    height: int,
    fps: Optional[int],
    fit_mode: str,
    bg_color: str,
    output_dir: str,
    phone_codename: Optional[str] = None,
    phone_name: Optional[str] = None,
    make_raw: bool = True,
    make_flashable: bool = True,
    make_restore: bool = True,
    make_magisk: bool = True
):
    start_time = time.time()
    base_name = os.path.splitext(os.path.basename(gif_path))[0]
    dev_tag = f"_{phone_codename}" if phone_codename else ""

    # Each boot animation has its own folder named after the GIF
    if os.path.basename(os.path.normpath(output_dir)).lower() != base_name.lower():
        output_dir = os.path.join(output_dir, base_name)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{Colors.HEADER}--- Processing Configuration ---{Colors.RESET}")
    print(f"  Input GIF:       {Colors.BOLD}{gif_path}{Colors.RESET}")
    if phone_name:
        print(f"  Phone Model:     {Colors.GREEN}{Colors.BOLD}{phone_name} ({phone_codename}){Colors.RESET}")
    print(f"  Resolution:      {Colors.CYAN}{width}x{height}{Colors.RESET}")
    print(f"  Fit Mode:        {fit_mode}")
    print(f"  Background:      {bg_color}")
    print(f"  Output Folder:   {output_dir}")

    # Initialize builder
    builder = BootAnimationBuilder(
        gif_path=gif_path,
        target_width=width,
        target_height=height,
        fps=fps,
        fit_mode=fit_mode,
        bg_color=bg_color
    )

    # Step 1: Extract and resize frames
    print(f"\n{Colors.GREEN}[1/5] Extracting & Resizing GIF Frames...{Colors.RESET}")
    frame_count = builder.extract_and_process_frames(progress_callback=print_progress)
    print(f"  {Colors.BOLD}Extracted {frame_count} frames | Frame Rate: {builder.calculated_fps} FPS{Colors.RESET}")

    # Step 2: Build raw bootanimation.zip
    print(f"\n{Colors.GREEN}[2/5] Packaging Uncompressed bootanimation.zip...{Colors.RESET}")
    raw_zip_path = os.path.join(output_dir, f"bootanimation{dev_tag}_{base_name}_{width}x{height}.zip")
    standalone_standard_path = os.path.join(output_dir, "bootanimation.zip")

    builder.build_bootanimation_zip(raw_zip_path)
    shutil.copyfile(raw_zip_path, standalone_standard_path)
    raw_size_mb = os.path.getsize(raw_zip_path) / (1024 * 1024)
    print(f"  -> Created: {Colors.BOLD}{standalone_standard_path}{Colors.RESET} ({raw_size_mb:.2f} MB)")
    if phone_codename:
        phone_raw_path = os.path.join(output_dir, f"bootanimation_{phone_codename}.zip")
        shutil.copyfile(raw_zip_path, phone_raw_path)
        print(f"  -> Created: {Colors.BOLD}{phone_raw_path}{Colors.RESET}")

    # Step 3: Build Rootless Flashable Recovery ZIP with Auto-Backup
    flashable_path = os.path.join(output_dir, f"bootanimation_flashable_rootless{dev_tag}_{base_name}.zip")
    if make_flashable:
        print(f"\n{Colors.GREEN}[3/5] Generating Rootless Flashable ZIP (with Auto-Backup)...{Colors.RESET}")
        builder.build_rootless_flashable_zip(
            bootanimation_zip_path=standalone_standard_path,
            output_flashable_path=flashable_path,
            device_name=phone_name or "",
            device_codename=phone_codename or ""
        )
        flash_size_mb = os.path.getsize(flashable_path) / (1024 * 1024)
        print(f"  -> Created: {Colors.BOLD}{flashable_path}{Colors.RESET} ({flash_size_mb:.2f} MB)")
        print(f"     {Colors.DIM}(Compatible with TWRP, OrangeFox, PBRP; backs up stock animation before replacing){Colors.RESET}")

    # Step 4: Build Standalone Restore Flashable ZIP
    restore_name = f"bootanimation_restore_flashable{dev_tag}.zip"
    restore_path = os.path.join(output_dir, restore_name)
    if make_restore:
        print(f"\n{Colors.GREEN}[4/5] Generating Standalone Restore ZIP...{Colors.RESET}")
        builder.build_restore_flashable_zip(
            output_restore_path=restore_path,
            device_name=phone_name or "",
            device_codename=phone_codename or ""
        )
        print(f"  -> Created: {Colors.BOLD}{restore_path}{Colors.RESET}")
        print(f"     {Colors.DIM}(Flash in TWRP anytime to revert back to stock bootanimation){Colors.RESET}")

    # Step 5: Build Magisk / KernelSU Module ZIP
    magisk_path = os.path.join(output_dir, f"bootanimation_magisk_module{dev_tag}_{base_name}.zip")
    if make_magisk:
        print(f"\n{Colors.GREEN}[5/5] Generating Systemless Magisk/KernelSU Module ZIP...{Colors.RESET}")
        builder.build_magisk_module_zip(
            bootanimation_zip_path=standalone_standard_path,
            output_magisk_path=magisk_path,
            device_name=phone_name or "",
            device_codename=phone_codename or ""
        )
        magisk_size_mb = os.path.getsize(magisk_path) / (1024 * 1024)
        print(f"  -> Created: {Colors.BOLD}{magisk_path}{Colors.RESET} ({magisk_size_mb:.2f} MB)")

    elapsed = time.time() - start_time
    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ Successfully completed in {elapsed:.2f} seconds!{Colors.RESET}\n")

    print(f"{Colors.HEADER}=== Generated Output Packages ==={Colors.RESET}")
    print(f"1. {Colors.BOLD}Rootless Recovery Flashable ZIP:{Colors.RESET}")
    print(f"   {Colors.CYAN}{flashable_path}{Colors.RESET}")
    print(f"   -> Flash in TWRP/OrangeFox. Automatically backs up your current bootanimation to /sdcard.")
    print(f"2. {Colors.BOLD}Recovery Restore ZIP:{Colors.RESET}")
    print(f"   {Colors.CYAN}{restore_path}{Colors.RESET}")
    print(f"   -> Flash in TWRP/OrangeFox anytime to restore the original backed up bootanimation.")
    print(f"3. {Colors.BOLD}Systemless Magisk / KernelSU Module:{Colors.RESET}")
    print(f"   {Colors.CYAN}{magisk_path}{Colors.RESET}")
    print(f"   -> Flash in Magisk Manager, KernelSU, APatch, or TWRP without touching system.")
    print(f"4. {Colors.BOLD}Raw Android bootanimation.zip:{Colors.RESET}")
    print(f"   {Colors.CYAN}{standalone_standard_path}{Colors.RESET}")
    print(f"   -> Uncompressed (STORED) ready for manual placement or ROM builders.\n")


# --- MAIN ENTRY POINT ---

def main():
    parser = argparse.ArgumentParser(
        description="Convert GIFs to Android bootanimations and produce rootless flashable ZIPs with automated backup.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-i", "--input", help="Path to input GIF file.")
    parser.add_argument(
        "-p", "--phone",
        help="Predefined phone codename or model (e.g. 'begonia', 'sweet', 'vayu', 'pixel8pro', 's24u').\nAutomatically sets resolution and configures device-tailored packages."
    )
    parser.add_argument(
        "--list-phones",
        action="store_true",
        help="Display all predefined phone models and codenames."
    )
    parser.add_argument(
        "-r", "--resolution",
        default=None,
        help="Target phone resolution (WIDTHxHEIGHT, e.g. 1080x2340, 1080x2400) or 'original'.\n(Overridden by --phone if specified)."
    )
    parser.add_argument("--fps", type=int, default=None, help="Target FPS (e.g. 30, 60). Default: phone preset or native GIF FPS.")
    parser.add_argument(
        "--fit",
        choices=["contain", "fit", "cover", "stretch", "center"],
        default="contain",
        help="Frame scaling mode:\n  contain: scale to fit screen, letterbox with background color\n  cover: fill entire screen, crop excess\n  stretch: non-uniform stretch\n  center: keep native size centered\nDefault: contain"
    )
    parser.add_argument("--bgcolor", default="#000000", help="Canvas background hex color (default: #000000).")
    parser.add_argument("-o", "--output-dir", default="./output", help="Directory to save generated ZIPs (default: ./output).")
    parser.add_argument("--no-flashable", action="store_true", help="Skip generating rootless recovery flashable ZIP.")
    parser.add_argument("--no-restore", action="store_true", help="Skip generating recovery restore ZIP.")
    parser.add_argument("--no-magisk", action="store_true", help="Skip generating Magisk module ZIP.")
    parser.add_argument("--batch", help="Path to directory containing multiple GIFs to convert in batch.")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive wizard.")

    args = parser.parse_args()

    # List predefined phones if requested
    if args.list_phones:
        list_predefined_phones()
        return

    # Launch interactive wizard if no arguments provided or explicitly requested
    if len(sys.argv) == 1 or args.interactive:
        run_interactive_wizard()
        return

    # Handle phone preset lookup
    phone_codename = None
    phone_name = None
    phone_fps = None
    width, height = None, None

    if args.phone:
        found = lookup_phone(args.phone)
        if not found:
            print(f"{Colors.RED}Unknown phone codename or model: '{args.phone}'{Colors.RESET}")
            print(f"Run {Colors.BOLD}python3 main.py --list-phones{Colors.RESET} to see all supported devices.")
            sys.exit(1)
        phone_codename, phone_data = found
        phone_name = phone_data["name"]
        width, height = phone_data["resolution"]
        phone_fps = phone_data.get("fps", 30)

    # Resolution override or fallback
    if args.resolution:
        width, height = parse_resolution(args.resolution, args.input)
    elif width is None or height is None:
        width, height = (1080, 2400)

    fps = args.fps if args.fps is not None else phone_fps
    fit_mode = "contain" if args.fit == "fit" else args.fit

    # Batch mode
    if args.batch:
        if not os.path.isdir(args.batch):
            print(f"{Colors.RED}Batch directory not found: {args.batch}{Colors.RESET}")
            sys.exit(1)
        gif_files = glob.glob(os.path.join(args.batch, "*.gif"))
        if not gif_files:
            print(f"{Colors.YELLOW}No GIF files found in {args.batch}{Colors.RESET}")
            sys.exit(0)
        print(f"Found {len(gif_files)} GIF files to batch convert...")
        for gif in gif_files:
            cur_w, cur_h = width, height
            if args.resolution == "original":
                cur_w, cur_h = parse_resolution("original", gif)
            execute_conversion(
                gif_path=gif,
                width=cur_w,
                height=cur_h,
                fps=fps,
                fit_mode=fit_mode,
                bg_color=args.bgcolor,
                output_dir=args.output_dir,
                phone_codename=phone_codename,
                phone_name=phone_name,
                make_raw=True,
                make_flashable=not args.no_flashable,
                make_restore=not args.no_restore,
                make_magisk=not args.no_magisk
            )
        return

    # Single file mode
    if not args.input:
        print(f"{Colors.RED}Error: --input GIF is required when running in non-interactive mode.{Colors.RESET}")
        print("Run with --help or --interactive for guided mode.")
        sys.exit(1)

    execute_conversion(
        gif_path=args.input,
        width=width,
        height=height,
        fps=fps,
        fit_mode=fit_mode,
        bg_color=args.bgcolor,
        output_dir=args.output_dir,
        phone_codename=phone_codename,
        phone_name=phone_name,
        make_raw=True,
        make_flashable=not args.no_flashable,
        make_restore=not args.no_restore,
        make_magisk=not args.no_magisk
    )


if __name__ == "__main__":
    main()
