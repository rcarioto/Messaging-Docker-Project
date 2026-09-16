#!/usr/bin/env python3
"""
RabbitMQ Messaging Examples
Demonstrates various messaging patterns using RabbitMQ
"""

import pika
import json
import time
import threading
from datetime import datetime

class RabbitMQMessaging:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            print(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("Connection closed")
    
    def simple_queue_example(self):
        """Simple queue example - direct messaging"""
        if not self.connect():
            return
        
        queue_name = 'simple_queue'
        
        # Declare queue
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        # Send message
        message = {
            'text': 'Hello from RabbitMQ!',
            'timestamp': datetime.now().isoformat(),
            'sender': 'python-producer'
        }
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        
        print(f"Sent message to queue '{queue_name}': {message['text']}")
        self.close()
    
    def simple_consumer_example(self):
        """Simple consumer example"""
        if not self.connect():
            return
        
        queue_name = 'simple_queue'
        
        # Declare queue
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                print(f"Received message: {message['text']}")
                print(f"Timestamp: {message['timestamp']}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except json.JSONDecodeError:
                print(f"Received raw message: {body}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # Set up consumer
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        
        print(f"Waiting for messages in queue '{queue_name}'. To exit press CTRL+C")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\nConsumer stopped")
            self.channel.stop_consuming()
        finally:
            self.close()
    
    def fanout_exchange_example(self):
        """Fanout exchange example - broadcast to all queues"""
        if not self.connect():
            return
        
        exchange_name = 'broadcast_exchange'
        queue_names = ['queue1', 'queue2', 'queue3']
        
        # Declare fanout exchange
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        
        # Declare queues and bind them to exchange
        for queue_name in queue_names:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(exchange=exchange_name, queue=queue_name)
        
        # Send broadcast message
        message = {
            'text': 'Broadcast message to all subscribers!',
            'timestamp': datetime.now().isoformat(),
            'sender': 'python-broadcaster'
        }
        
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key='',  # routing key is ignored for fanout
            body=json.dumps(message)
        )
        
        print(f"Broadcasted message to {len(queue_names)} queues: {message['text']}")
        self.close()
    
    def topic_exchange_example(self):
        """Topic exchange example - routing based on patterns"""
        if not self.connect():
            return
        
        exchange_name = 'topic_exchange'
        
        # Declare topic exchange
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
        
        # Define routing patterns and queues
        routing_patterns = {
            'news.sports': 'sports_queue',
            'news.weather': 'weather_queue',
            'news.technology': 'tech_queue',
            'alerts.system': 'system_queue',
            'alerts.user': 'user_queue'
        }
        
        # Declare queues and bind with routing keys
        for routing_key, queue_name in routing_patterns.items():
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        
        # Send messages with different routing keys
        messages = [
            ('news.sports', 'Sports news: Team wins championship!'),
            ('news.weather', 'Weather update: Sunny with clear skies'),
            ('news.technology', 'Tech news: New AI breakthrough'),
            ('alerts.system', 'System alert: Maintenance scheduled'),
            ('alerts.user', 'User notification: Welcome to our platform')
        ]
        
        for routing_key, text in messages:
            message = {
                'text': text,
                'timestamp': datetime.now().isoformat(),
                'routing_key': routing_key,
                'sender': 'python-topic-producer'
            }
            
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message)
            )
            
            print(f"Sent message with routing key '{routing_key}': {text}")
        
        self.close()
    
    def topic_consumer_example(self, queue_name):
        """Topic consumer example"""
        if not self.connect():
            return
        
        exchange_name = 'topic_exchange'
        
        # Declare topic exchange
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
        
        # Declare queue
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                print(f"[{queue_name}] Received: {message['text']}")
                print(f"Routing key: {message.get('routing_key', 'N/A')}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except json.JSONDecodeError:
                print(f"[{queue_name}] Received raw message: {body}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        # Set up consumer
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        
        print(f"Waiting for messages in queue '{queue_name}'. To exit press CTRL+C")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print(f"\nConsumer for {queue_name} stopped")
            self.channel.stop_consuming()
        finally:
            self.close()
    
    def rpc_example(self):
        """RPC (Remote Procedure Call) example"""
        if not self.connect():
            return
        
        # Declare callback queue for RPC
        result = self.channel.queue_declare(queue='', exclusive=True)
        callback_queue = result.method.queue
        
        # Generate correlation ID
        correlation_id = str(time.time())
        
        # Send RPC request
        message = {
            'number': 10,
            'operation': 'fibonacci'
        }
        
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=correlation_id,
            ),
            body=json.dumps(message)
        )
        
        print(f"Sent RPC request: {message}")
        
        # Wait for response
        response_received = False
        
        def callback(ch, method, properties, body):
            nonlocal response_received
            if properties.correlation_id == correlation_id:
                try:
                    response = json.loads(body)
                    print(f"RPC Response: {response}")
                    response_received = True
                except json.JSONDecodeError:
                    print(f"RPC Response (raw): {body}")
                    response_received = True
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_consume(queue=callback_queue, on_message_callback=callback)
        
        # Wait for response with timeout
        timeout = 10  # seconds
        start_time = time.time()
        
        while not response_received and (time.time() - start_time) < timeout:
            self.connection.process_data_events(time_limit=1)
        
        if not response_received:
            print("RPC response timeout")
        
        self.close()
    
    def rpc_server_example(self):
        """RPC server example"""
        if not self.connect():
            return
        
        # Declare RPC queue
        self.channel.queue_declare(queue='rpc_queue')
        
        def fibonacci(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            else:
                return fibonacci(n - 1) + fibonacci(n - 2)
        
        def callback(ch, method, properties, body):
            try:
                request = json.loads(body)
                number = request.get('number', 0)
                operation = request.get('operation', 'unknown')
                
                if operation == 'fibonacci':
                    result = fibonacci(number)
                    response = {
                        'result': result,
                        'input': number,
                        'operation': operation
                    }
                else:
                    response = {
                        'error': f'Unknown operation: {operation}'
                    }
                
                ch.basic_publish(
                    exchange='',
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps(response)
                )
                
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                response = {'error': str(e)}
                ch.basic_publish(
                    exchange='',
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps(response)
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='rpc_queue', on_message_callback=callback)
        
        print("RPC Server started. Waiting for requests...")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\nRPC Server stopped")
            self.channel.stop_consuming()
        finally:
            self.close()

def run_examples():
    """Run different RabbitMQ examples"""
    messaging = RabbitMQMessaging()
    
    while True:
        print("\nRabbitMQ Messaging Examples")
        print("=" * 40)
        print("1. Simple Queue Producer")
        print("2. Simple Queue Consumer")
        print("3. Fanout Exchange (Broadcast)")
        print("4. Topic Exchange Producer")
        print("5. Topic Exchange Consumer")
        print("6. RPC Client")
        print("7. RPC Server")
        print("8. Exit")
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            messaging.simple_queue_example()
        elif choice == '2':
            messaging.simple_consumer_example()
        elif choice == '3':
            messaging.fanout_exchange_example()
        elif choice == '4':
            messaging.topic_exchange_example()
        elif choice == '5':
            queue_name = input("Enter queue name (sports_queue/weather_queue/tech_queue/system_queue/user_queue): ").strip()
            if queue_name:
                messaging.topic_consumer_example(queue_name)
        elif choice == '6':
            messaging.rpc_example()
        elif choice == '7':
            messaging.rpc_server_example()
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    run_examples() 