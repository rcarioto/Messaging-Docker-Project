#!/usr/bin/env python3
"""
Zyre Demo Example
Zyre is a distributed messaging framework built on ZeroMQ
"""

import zyre
import time
import threading

class ZyreDemo:
    def __init__(self, node_name):
        self.node_name = node_name
        self.node = zyre.Zyre(node_name)
        self.running = False
        
    def start(self):
        """Start the Zyre node"""
        self.node.start()
        self.running = True
        print(f"Zyre node '{self.node_name}' started")
        
        # Join a demo group
        self.node.join("demo-group")
        print("Joined 'demo-group'")
        
    def stop(self):
        """Stop the Zyre node"""
        self.running = False
        self.node.stop()
        print(f"Zyre node '{self.node_name}' stopped")
        
    def send_message(self, message):
        """Send a message to the group"""
        if self.running:
            self.node.shout("demo-group", message)
            print(f"Sent: {message}")
            
    def receive_messages(self):
        """Receive and print messages"""
        while self.running:
            try:
                event = self.node.recv()
                if event:
                    event_type = event.get_type()
                    if event_type == "SHOUT":
                        sender = event.get_peer_name()
                        group = event.get_group()
                        message = event.get_msg().popstr()
                        print(f"Received from {sender} in {group}: {message}")
                    elif event_type == "ENTER":
                        peer = event.get_peer_name()
                        print(f"Peer {peer} entered")
                    elif event_type == "EXIT":
                        peer = event.get_peer_name()
                        print(f"Peer {peer} exited")
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                    
    def run_demo(self, duration=30):
        """Run the demo for a specified duration"""
        self.start()
        
        # Start message receiver in a separate thread
        receiver_thread = threading.Thread(target=self.receive_messages)
        receiver_thread.daemon = True
        receiver_thread.start()
        
        # Send messages periodically
        message_count = 0
        start_time = time.time()
        
        while time.time() - start_time < duration:
            message_count += 1
            message = f"Hello from {self.node_name}! Message #{message_count}"
            self.send_message(message)
            time.sleep(5)
            
        self.stop()

def main():
    # Create and run demo
    demo = ZyreDemo("demo-node-1")
    
    try:
        print("Starting Zyre demo (30 seconds)...")
        demo.run_demo(30)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        demo.stop()
    except Exception as e:
        print(f"Demo error: {e}")
        demo.stop()

if __name__ == "__main__":
    main() 