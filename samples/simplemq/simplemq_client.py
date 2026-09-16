#!/usr/bin/env python3
"""
SimpleMQ Client Example
SimpleMQ is a simple message queue system with HTTP API
"""

import requests
import json
import time

class SimpleMQClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def send_message(self, message):
        """Send a message to SimpleMQ"""
        url = f"{self.base_url}/send"
        payload = {"message": message}
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"Message sent: {message}")
                return response.json()
            else:
                print(f"Failed to send message: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            return None
    
    def get_messages(self):
        """Get all messages from SimpleMQ"""
        url = f"{self.base_url}/messages"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get messages: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting messages: {e}")
            return None
    
    def clear_messages(self):
        """Clear all messages"""
        url = f"{self.base_url}/clear"
        
        try:
            response = requests.post(url)
            if response.status_code == 200:
                print("Messages cleared")
                return True
            else:
                print(f"Failed to clear messages: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error clearing messages: {e}")
            return False

def main():
    client = SimpleMQClient()
    
    # Send some messages
    messages = [
        "Hello from SimpleMQ!",
        "This is a simple message queue",
        "Easy to use and setup",
        "Perfect for real-time messaging"
    ]
    
    print("Sending messages to SimpleMQ...")
    for i, message in enumerate(messages, 1):
        client.send_message(f"{i}. {message}")
        time.sleep(1)
    
    # Get all messages
    print("\nGetting all messages...")
    all_messages = client.get_messages()
    if all_messages:
        print(f"All messages: {json.dumps(all_messages, indent=2)}")
    
    # Clear messages
    print("\nClearing messages...")
    client.clear_messages()

if __name__ == "__main__":
    main() 