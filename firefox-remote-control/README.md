# Firefox Remote Control Extension

Control your Firefox browser from Python scripts.

## Installation Steps

### 1. Install the Firefox Extension

1. Open Firefox
2. Type `about:debugging` in the address bar
3. Click "This Firefox" in the left sidebar
4. Click "Load Temporary Add-on"
5. Navigate to `/home/yousef/multi-dictate/firefox-remote-control/`
6. Select `manifest.json`

The extension is now loaded!

### 2. Native Messaging is Already Configured

The native messaging host has been installed to:
`~/.mozilla/native-messaging-hosts/browser_remote_control.json`

## Usage

### From Python:

```python
from browser_control import BrowserControl
import time

# Connect to Firefox
browser = BrowserControl()
browser.connect()

# Open a URL
browser.open_url("https://github.com/zonevast/multi-dictate")
time.sleep(2)

# Get current URL
url = browser.get_url()
print(f"Current URL: {url}")

# Get page HTML
html = browser.get_html()
print(html[:500])

# Execute JavaScript
result = browser.execute_script("document.title")
print(f"Page title: {result}")

# Close tab
browser.close_tab()

# Disconnect
browser.disconnect()
```

### Available Commands:

- `open_url(url)` - Open URL in new tab
- `get_html()` - Get HTML of active tab
- `get_url()` - Get URL of active tab
- `execute_script(code)` - Execute JavaScript in active tab
- `close_tab()` - Close active tab

## Testing

Run the test:
```bash
cd /home/yousef/multi-dictate/firefox-remote-control
python3 browser_control.py
```

This will:
1. Open GitHub
2. Get the current URL
3. Get the page HTML
4. Print results
