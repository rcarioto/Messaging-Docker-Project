#!/usr/bin/env python3
"""
Hermes Client Example
Hermes is a message broker built on top of Kafka with REST API
"""

import requests
import json
import time

class HermesClient:
    def __init__(self, base_url="http://localhost:8086"):
        self.base_url = base_url
        
    def publish_message(self, topic, message):
        """Publish a message to a topic"""
        url = f"{self.base_url}/topics/{topic}"
        payload = {
            "message": message,
            "timestamp": int(time.time() * 1000)
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                print(f"Message published to topic '{topic}': {message}")
                return response.json()
            else:
                print(f"Failed to publish message: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error publishing message: {e}")
            return None
    
    def get_topic_info(self, topic):
        """Get information about a topic"""
        url = f"{self.base_url}/topics/{topic}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get topic info: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting topic info: {e}")
            return None

def main():
    client = HermesClient()
    
    # Example topic
    topic = "demo-topic"
    
    # Publish some messages
    messages = [
        "Hello from Hermes!",
        "This is a test message",
        "Hermes is awesome!",
        "Built on top of Kafka"
    ]
    
    print("Publishing messages to Hermes...")
    for i, message in enumerate(messages, 1):
        client.publish_message(topic, f"{i}. {message}")
        time.sleep(1)
    
    # Get topic information
    print(f"\nGetting info for topic '{topic}'...")
    topic_info = client.get_topic_info(topic)
    if topic_info:
        print(f"Topic info: {json.dumps(topic_info, indent=2)}")

if __name__ == "__main__":
    main() 