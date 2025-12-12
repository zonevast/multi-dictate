#!/usr/bin/env python3
"""
Simple Python API to control Firefox browser
Usage example:

from browser_control import BrowserControl

browser = BrowserControl()
browser.open_url("https://github.com")
html = browser.get_html()
print(html)
"""
import subprocess
import json
import struct
import threading
import queue
import time

class BrowserControl:
    def __init__(self):
        self.process = None
        self.response_queue = queue.Queue()
        self.message_id = 0

    def connect(self):
        """Connect to Firefox via native messaging host"""
        self.process = subprocess.Popen(
            ['python3', 'native_host.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='/home/yousef/multi-dictate/firefox-remote-control'
        )

        # Start listener thread
        self.listener = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener.start()
        time.sleep(0.5)  # Give it time to start

    def _send_message(self, message):
        """Send message to native host"""
        if not self.process:
            raise Exception("Not connected. Call connect() first.")

        encoded_content = json.dumps(message).encode('utf-8')
        encoded_length = struct.pack('I', len(encoded_content))
        self.process.stdin.write(encoded_length)
        self.process.stdin.write(encoded_content)
        self.process.stdin.flush()

    def _listen_loop(self):
        """Listen for responses from native host"""
        while self.process and self.process.poll() is None:
            try:
                raw_length = self.process.stdout.read(4)
                if len(raw_length) == 0:
                    break
                message_length = struct.unpack('I', raw_length)[0]
                message = self.process.stdout.read(message_length).decode('utf-8')
                response = json.loads(message)
                self.response_queue.put(response)
            except Exception as e:
                print(f"Error in listen loop: {e}")
                break

    def _send_command(self, action, **kwargs):
        """Send command and wait for response"""
        self.message_id += 1
        message = {
            'id': self.message_id,
            'action': action,
            **kwargs
        }
        self._send_message(message)

        # Wait for response
        try:
            response = self.response_queue.get(timeout=5)
            return response
        except queue.Empty:
            return {'success': False, 'error': 'Timeout waiting for response'}

    def open_url(self, url):
        """Open URL in new tab"""
        return self._send_command('open_url', url=url)

    def get_html(self):
        """Get HTML of active tab"""
        response = self._send_command('get_html')
        if response.get('success'):
            return response.get('html', '')
        return None

    def execute_script(self, code):
        """Execute JavaScript in active tab"""
        response = self._send_command('execute_script', code=code)
        if response.get('success'):
            return response.get('result')
        return None

    def get_url(self):
        """Get URL of active tab"""
        response = self._send_command('get_url')
        if response.get('success'):
            return response.get('url', '')
        return None

    def close_tab(self):
        """Close active tab"""
        return self._send_command('close_tab')

    def disconnect(self):
        """Close connection"""
        if self.process:
            self.process.terminate()
            self.process = None

# Example usage
if __name__ == '__main__':
    browser = BrowserControl()
    browser.connect()

    print("Opening GitHub...")
    result = browser.open_url("https://github.com")
    print(result)

    time.sleep(2)

    print("\nGetting current URL...")
    url = browser.get_url()
    print(f"Current URL: {url}")

    print("\nGetting HTML (first 500 chars)...")
    html = browser.get_html()
    if html:
        print(html[:500])

    browser.disconnect()
