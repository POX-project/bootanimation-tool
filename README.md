# POX PROJECT - Bootanimation Tool

[![CI](https://github.com/POX-project/bootanimation-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/POX-project/bootanimation-tool/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/POX-project/bootanimation-tool?color=brightgreen)](https://github.com/POX-project/bootanimation-tool/releases)

**Maintainer:** **`txorav`** • **Platform:** Linux / macOS / Windows (Python 3.8+)

A powerful, rootless generator and packager that converts animated GIFs into Android `bootanimation.zip` animations for any phone resolution and packages them into **recovery-flashable ZIPs with automated backup & restore** capabilities.

Compatible with **TWRP, OrangeFox, PBRP, SHRP**, as well as **Magisk, KernelSU, APatch**, and standalone ROM building.

---

## Features

- 📱 **Predefined Phone Database**: Dedicated presets for popular phones like **Redmi Note 8 Pro (`begonia`)**, POCO (`vayu`, `sweet`, `alioth`, `marble`, `peridot`), Google Pixel (`husky`, `cheetah`, `raven`, `redfin`), Samsung Galaxy (`s24u`, `s23u`, `s22u`, `s21`, `a54`), OnePlus, Nothing Phone, etc.
- 🔒 **100% Rootless Recovery Flashable ZIP**: Flashable directly in custom recovery (TWRP/OrangeFox) without needing root or Magisk installed.
- 💾 **Intelligent Automatic Backup**:
  - Automatically scans `/product/media`, `/system/product/media`, `/system/media`, `/system_ext/media`, `/oem/media`, and `/data/local`.
  - Creates an in-place backup (`.bak`).
  - Creates a timestamped backup and master backup in `/sdcard/BootAnimation_Backups/` (with metadata & MD5 hash).
  - Automatically generates an executable restore script (`restore_bootanimation.sh`) on your device.
- 🔄 **One-Flash Restore ZIP**: Packages an accompanying `bootanimation_restore_flashable.zip` so you can revert to your stock animation anytime with one click in recovery.
- ⚡ **Zero-Compression Standard (`STORED`)**: Strict compliance with Android's native bootanimation engine.
- 🛡️ **Dynamic Partition & SAR Resilient**: Remounts `/system` and `/product` read-write, with automatic fallback to `/data/local/bootanimation.zip` if dynamic partitions are locked/read-only (EROFS).
- 🧩 **Magisk / KernelSU / APatch Module**: Also generates a systemless module for rooted users who prefer not modifying system partitions.
- 🎨 **Smart Scaling Modes**: `contain` (aspect ratio preserved, AMOLED black letterbox), `cover` (fullscreen cropped), `stretch`, and `center`.

---

## Installation

```bash
git clone https://github.com/POX-project/bootanimation-tool.git
cd bootanimation-tool
pip install -r requirements.txt
```

---

## Usage

### 1. Convert for Redmi Note 8 Pro (`begonia`)
```bash
python3 main.py -i gifs/BLYkag.gif -p begonia
```

### 2. Interactive Wizard (Guided UI)
Run without arguments to launch the interactive setup wizard:
```bash
python3 main.py
```

### 3. Custom Resolution
```bash
python3 main.py -i animation.gif -w 1080 -H 2400 --fps 30 -s contain
```

### 4. List All Predefined Phone Codenames
```bash
python3 main.py --list-phones
```

---

## 🇵🇸 Solidarity
**FREE PALESTINE** — Support justice, end oppression, and spread awareness on all matters of shared humanity.
