#!/usr/bin/env python3
"""
Redis Pub/Sub Messaging Example
Demonstrates publisher-subscriber pattern using Redis
"""

import redis
import time
import threading
import json
from datetime import datetime

class RedisMessaging:
    def __init__(self, host='localhost', port=6379):
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
    def publish_message(self, channel, message):
        """Publish a message to a specific channel"""
        try:
            # Create message with timestamp
            message_data = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'sender': 'python-client'
            }
            
            # Publish JSON message
            result = self.redis_client.publish(channel, json.dumps(message_data))
            print(f"Published message to channel '{channel}': {message}")
            print(f"Number of subscribers: {result}")
            return result
        except Exception as e:
            print(f"Error publishing message: {e}")
            return None
    
    def subscribe_to_channel(self, channel, callback=None):
        """Subscribe to a channel and listen for messages"""
        def default_callback(message):
            try:
                data = json.loads(message['data'])
                print(f"[{data['timestamp']}] Channel '{channel}': {data['message']}")
            except json.JSONDecodeError:
                print(f"[{datetime.now().isoformat()}] Channel '{channel}': {message['data']}")
        
        if callback is None:
            callback = default_callback
            
        try:
            self.pubsub.subscribe(channel)
            print(f"Subscribed to channel: {channel}")
            
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    callback(message)
                elif message['type'] == 'subscribe':
                    print(f"Successfully subscribed to {message['channel']}")
                    
        except KeyboardInterrupt:
            print("\nUnsubscribing...")
            self.pubsub.unsubscribe(channel)
        except Exception as e:
            print(f"Error in subscription: {e}")
    
    def pattern_subscribe(self, pattern, callback=None):
        """Subscribe to channels matching a pattern"""
        def default_callback(message):
            try:
                data = json.loads(message['data'])
                print(f"[{data['timestamp']}] Pattern '{pattern}' -> Channel '{message['channel']}': {data['message']}")
            except json.JSONDecodeError:
                print(f"[{datetime.now().isoformat()}] Pattern '{pattern}' -> Channel '{message['channel']}': {message['data']}")
        
        if callback is None:
            callback = default_callback
            
        try:
            self.pubsub.psubscribe(pattern)
            print(f"Subscribed to pattern: {pattern}")
            
            for message in self.pubsub.listen():
                if message['type'] == 'pmessage':
                    callback(message)
                elif message['type'] == 'psubscribe':
                    print(f"Successfully subscribed to pattern {message['pattern']}")
                    
        except KeyboardInterrupt:
            print("\nUnsubscribing from pattern...")
            self.pubsub.punsubscribe(pattern)
        except Exception as e:
            print(f"Error in pattern subscription: {e}")
    
    def close(self):
        """Close the Redis connection"""
        self.pubsub.close()
        self.redis_client.close()

def publisher_example():
    """Example publisher function"""
    messaging = RedisMessaging()
    
    channels = ['news', 'weather', 'sports']
    messages = [
        "Breaking news: New technology breakthrough!",
        "Weather update: Sunny with clear skies",
        "Sports update: Team wins championship!",
        "System alert: Maintenance scheduled",
        "User notification: Welcome to our platform"
    ]
    
    try:
        for i in range(10):
            channel = channels[i % len(channels)]
            message = messages[i % len(messages)]
            messaging.publish_message(channel, f"{message} (Message #{i+1})")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPublisher stopped")
    finally:
        messaging.close()

def subscriber_example():
    """Example subscriber function"""
    messaging = RedisMessaging()
    
    try:
        # Subscribe to specific channels
        print("Starting subscriber...")
        messaging.subscribe_to_channel('news')
    except KeyboardInterrupt:
        print("\nSubscriber stopped")
    finally:
        messaging.close()

def pattern_subscriber_example():
    """Example pattern subscriber function"""
    messaging = RedisMessaging()
    
    try:
        # Subscribe to all channels starting with 'w'
        print("Starting pattern subscriber...")
        messaging.pattern_subscribe('w*')
    except KeyboardInterrupt:
        print("\nPattern subscriber stopped")
    finally:
        messaging.close()

def multi_threaded_example():
    """Example with multiple threads"""
    messaging = RedisMessaging()
    
    def news_subscriber():
        messaging.subscribe_to_channel('news')
    
    def weather_subscriber():
        messaging.subscribe_to_channel('weather')
    
    def sports_subscriber():
        messaging.subscribe_to_channel('sports')
    
    # Start subscriber threads
    threads = []
    for subscriber_func in [news_subscriber, weather_subscriber, sports_subscriber]:
        thread = threading.Thread(target=subscriber_func)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Wait a bit for subscribers to connect
    time.sleep(2)
    
    # Publish messages
    try:
        for i in range(5):
            messaging.publish_message('news', f"News message #{i+1}")
            messaging.publish_message('weather', f"Weather update #{i+1}")
            messaging.publish_message('sports', f"Sports news #{i+1}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nMulti-threaded example stopped")
    finally:
        messaging.close()

if __name__ == "__main__":
    print("Redis Pub/Sub Messaging Examples")
    print("=" * 40)
    
    while True:
        print("\nChoose an example:")
        print("1. Publisher Example")
        print("2. Subscriber Example")
        print("3. Pattern Subscriber Example")
        print("4. Multi-threaded Example")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\nRunning Publisher Example...")
            publisher_example()
        elif choice == '2':
            print("\nRunning Subscriber Example...")
            subscriber_example()
        elif choice == '3':
            print("\nRunning Pattern Subscriber Example...")
            pattern_subscriber_example()
        elif choice == '4':
            print("\nRunning Multi-threaded Example...")
            multi_threaded_example()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.") 