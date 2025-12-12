#!/usr/bin/env python3
"""
Native messaging host for Firefox browser control
Communicates with the Firefox extension via stdin/stdout
"""
import sys
import json
import struct
import threading
import queue

class BrowserController:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.message_id = 0

    def send_message(self, message):
        """Send message to Firefox extension"""
        encoded_content = json.dumps(message).encode('utf-8')
        encoded_length = struct.pack('I', len(encoded_content))
        sys.stdout.buffer.write(encoded_length)
        sys.stdout.buffer.write(encoded_content)
        sys.stdout.buffer.flush()

    def receive_message(self):
        """Receive message from Firefox extension"""
        raw_length = sys.stdin.buffer.read(4)
        if len(raw_length) == 0:
            return None
        message_length = struct.unpack('I', raw_length)[0]
        message = sys.stdin.buffer.read(message_length).decode('utf-8')
        return json.loads(message)

    def listen_loop(self):
        """Listen for responses from Firefox"""
        while True:
            try:
                response = self.receive_message()
                if response is None:
                    break
                self.response_queue.put(response)
            except Exception as e:
                sys.stderr.write(f"Error in listen loop: {e}\n")
                sys.stderr.flush()
                break

    def send_command(self, action, **kwargs):
        """Send command to Firefox and wait for response"""
        self.message_id += 1
        message = {
            'id': self.message_id,
            'action': action,
            **kwargs
        }
        self.send_message(message)

        # Wait for response (with timeout)
        try:
            response = self.response_queue.get(timeout=5)
            return response
        except queue.Empty:
            return {'success': False, 'error': 'Timeout waiting for response'}

    def open_url(self, url):
        """Open URL in new tab"""
        return self.send_command('open_url', url=url)

    def get_html(self):
        """Get HTML of active tab"""
        return self.send_command('get_html')

    def execute_script(self, code):
        """Execute JavaScript in active tab"""
        return self.send_command('execute_script', code=code)

    def get_url(self):
        """Get URL of active tab"""
        return self.send_command('get_url')

    def close_tab(self):
        """Close active tab"""
        return self.send_command('close_tab')

def main():
    """Main entry point for native messaging"""
    controller = BrowserController()

    # Start listening thread
    listener = threading.Thread(target=controller.listen_loop, daemon=True)
    listener.start()

    # Send ready message
    sys.stderr.write("Native host ready\n")
    sys.stderr.flush()

    # Keep alive
    listener.join()

if __name__ == '__main__':
    main()
