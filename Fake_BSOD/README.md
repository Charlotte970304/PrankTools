# Fake BSOD Loader
A simple full-screen prank tool that displays a Windows-style blue screen  
with a simulated loading progress and ends with a friendly “Surprise!” message.

---

## Requirements

This tool requires the following Python packages:

```
pillow>=9.0.0
qrcode[pil]>=7.3
```

Install with:

```bash
pip install -r requirements.txt
```
---
Python Version

Works on Python 3.9–3.13
Tested on Python 3.13.3
---

Configuration

Edit bsod_config.json:

```json
{
    "delay_seconds": 5,
    "percent_speed": 80,
    "hold_after_100": 3
}

```
Run

```bash
python main.py
```
Press ESC at any time to exit.