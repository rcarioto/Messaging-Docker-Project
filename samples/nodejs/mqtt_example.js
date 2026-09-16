#!/usr/bin/env node

/**
 * MQTT Messaging Examples
 * Demonstrates various MQTT patterns using Node.js
 */

const mqtt = require('mqtt');
const readline = require('readline');

class MQTTMessaging {
    constructor(brokerUrl = 'mqtt://localhost:1883') {
        this.brokerUrl = brokerUrl;
        this.client = null;
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    /**
     * Connect to MQTT broker
     */
    connect() {
        return new Promise((resolve, reject) => {
            const options = {
                clientId: `mqtt_client_${Math.random().toString(16).slice(3)}`,
                clean: true,
                connectTimeout: 4000,
                username: 'guest',
                password: 'guest',
                reconnectPeriod: 1000,
            };

            this.client = mqtt.connect(this.brokerUrl, options);

            this.client.on('connect', () => {
                console.log(`Connected to MQTT broker at ${this.brokerUrl}`);
                resolve();
            });

            this.client.on('error', (err) => {
                console.error('MQTT connection error:', err);
                reject(err);
            });

            this.client.on('close', () => {
                console.log('MQTT connection closed');
            });

            this.client.on('reconnect', () => {
                console.log('MQTT reconnecting...');
            });
        });
    }

    /**
     * Disconnect from MQTT broker
     */
    disconnect() {
        if (this.client) {
            this.client.end();
            this.client = null;
        }
        if (this.rl) {
            this.rl.close();
        }
    }

    /**
     * Publish a message to a topic
     */
    publish(topic, message, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.client) {
                reject(new Error('Not connected to MQTT broker'));
                return;
            }

            const messageObj = {
                content: message,
                timestamp: new Date().toISOString(),
                sender: 'nodejs-client',
                ...options
            };

            const payload = JSON.stringify(messageObj);

            this.client.publish(topic, payload, { qos: options.qos || 0 }, (err) => {
                if (err) {
                    console.error('Error publishing message:', err);
                    reject(err);
                } else {
                    console.log(`Published to '${topic}': ${message}`);
                    resolve();
                }
            });
        });
    }

    /**
     * Subscribe to a topic
     */
    subscribe(topic, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.client) {
                reject(new Error('Not connected to MQTT broker'));
                return;
            }

            this.client.subscribe(topic, { qos: options.qos || 0 }, (err) => {
                if (err) {
                    console.error('Error subscribing to topic:', err);
                    reject(err);
                } else {
                    console.log(`Subscribed to topic: ${topic}`);
                    resolve();
                }
            });
        });
    }

    /**
     * Set up message handler
     */
    onMessage(callback) {
        if (!this.client) {
            throw new Error('Not connected to MQTT broker');
        }

        this.client.on('message', (topic, message) => {
            try {
                const messageObj = JSON.parse(message.toString());
                callback(topic, messageObj);
            } catch (err) {
                console.log(`Received raw message on '${topic}': ${message.toString()}`);
                callback(topic, { content: message.toString() });
            }
        });
    }

    /**
     * Simple publisher example
     */
    async simplePublisherExample() {
        console.log('\n=== Simple Publisher Example ===');
        
        try {
            await this.connect();
            
            const topics = ['sensor/temperature', 'sensor/humidity', 'sensor/pressure'];
            const messages = [
                'Temperature: 25.5°C',
                'Humidity: 60%',
                'Pressure: 1013.25 hPa'
            ];

            for (let i = 0; i < 10; i++) {
                const topic = topics[i % topics.length];
                const message = `${messages[i % messages.length]} (reading #${i + 1})`;
                
                await this.publish(topic, message, { qos: 1 });
                await this.sleep(1000);
            }

        } catch (err) {
            console.error('Error in simple publisher:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * Simple subscriber example
     */
    async simpleSubscriberExample() {
        console.log('\n=== Simple Subscriber Example ===');
        
        try {
            await this.connect();
            
            const topic = 'sensor/temperature';
            await this.subscribe(topic, { qos: 1 });

            this.onMessage((topic, message) => {
                console.log(`[${topic}] ${message.content} (from ${message.sender || 'unknown'} at ${message.timestamp || 'unknown'})`);
            });

            console.log(`Listening for messages on '${topic}'. Press Ctrl+C to stop...`);
            
            // Keep the connection alive
            await this.waitForInterrupt();

        } catch (err) {
            console.error('Error in simple subscriber:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * Wildcard subscriber example
     */
    async wildcardSubscriberExample() {
        console.log('\n=== Wildcard Subscriber Example ===');
        
        try {
            await this.connect();
            
            const topic = 'sensor/#';
            await this.subscribe(topic, { qos: 1 });

            this.onMessage((topic, message) => {
                console.log(`[${topic}] ${message.content} (from ${message.sender || 'unknown'})`);
            });

            console.log(`Listening for messages on wildcard '${topic}'. Press Ctrl+C to stop...`);
            
            await this.waitForInterrupt();

        } catch (err) {
            console.error('Error in wildcard subscriber:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * QoS levels example
     */
    async qosLevelsExample() {
        console.log('\n=== QoS Levels Example ===');
        
        try {
            await this.connect();
            
            const topic = 'qos/test';
            const message = 'Testing different QoS levels';
            
            // Test QoS 0 (At most once)
            console.log('Publishing with QoS 0...');
            await this.publish(topic, `${message} - QoS 0`, { qos: 0 });
            
            // Test QoS 1 (At least once)
            console.log('Publishing with QoS 1...');
            await this.publish(topic, `${message} - QoS 1`, { qos: 1 });
            
            // Test QoS 2 (Exactly once)
            console.log('Publishing with QoS 2...');
            await this.publish(topic, `${message} - QoS 2`, { qos: 2 });

        } catch (err) {
            console.error('Error in QoS levels example:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * Retained messages example
     */
    async retainedMessagesExample() {
        console.log('\n=== Retained Messages Example ===');
        
        try {
            await this.connect();
            
            const topic = 'status/system';
            const message = 'System is online and operational';
            
            // Publish retained message
            console.log('Publishing retained message...');
            await this.publish(topic, message, { 
                qos: 1, 
                retain: true 
            });
            
            console.log('Retained message published. New subscribers will receive this message immediately.');

        } catch (err) {
            console.error('Error in retained messages example:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * Will and Testament example
     */
    async willAndTestamentExample() {
        console.log('\n=== Will and Testament Example ===');
        
        try {
            await this.connect();
            
            const willTopic = 'status/client';
            const willMessage = 'Client disconnected unexpectedly';
            
            // Set up will and testament
            this.client.options.will = {
                topic: willTopic,
                payload: JSON.stringify({
                    content: willMessage,
                    timestamp: new Date().toISOString(),
                    sender: 'nodejs-client'
                }),
                qos: 1,
                retain: false
            };
            
            console.log('Will and testament configured. If this client disconnects unexpectedly,');
            console.log(`a message will be published to '${willTopic}'.`);
            
            // Subscribe to will topic to see the message
            await this.subscribe(willTopic);
            
            this.onMessage((topic, message) => {
                console.log(`[${topic}] ${message.content}`);
            });
            
            console.log('Press Enter to disconnect normally (no will message), or Ctrl+C to disconnect unexpectedly...');
            await this.waitForUserInput();

        } catch (err) {
            console.error('Error in will and testament example:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * Multiple topics publisher example
     */
    async multipleTopicsPublisherExample() {
        console.log('\n=== Multiple Topics Publisher Example ===');
        
        try {
            await this.connect();
            
            const topics = [
                'home/living-room/temperature',
                'home/kitchen/temperature',
                'home/bedroom/temperature',
                'home/garage/temperature'
            ];
            
            const temperatures = [22.5, 24.0, 21.8, 18.2];
            
            for (let i = 0; i < topics.length; i++) {
                const topic = topics[i];
                const temp = temperatures[i];
                const message = `Temperature: ${temp}°C`;
                
                await this.publish(topic, message, { qos: 1 });
                console.log(`Published to ${topic}: ${message}`);
                await this.sleep(500);
            }

        } catch (err) {
            console.error('Error in multiple topics publisher:', err);
        } finally {
            this.disconnect();
        }
    }

    /**
     * Interactive publisher
     */
    async interactivePublisher() {
        console.log('\n=== Interactive Publisher ===');
        
        try {
            await this.connect();
            
            console.log('Enter messages to publish (format: topic:message)');
            console.log('Example: sensor/temp:Temperature is 25°C');
            console.log('Type "quit" to exit');
            
            const askQuestion = () => {
                this.rl.question('Enter topic:message: ', async (input) => {
                    if (input.toLowerCase() === 'quit') {
                        this.disconnect();
                        return;
                    }
                    
                    const parts = input.split(':');
                    if (parts.length !== 2) {
                        console.log('Invalid format. Use: topic:message');
                        askQuestion();
                        return;
                    }
                    
                    const [topic, message] = parts;
                    try {
                        await this.publish(topic.trim(), message.trim(), { qos: 1 });
                    } catch (err) {
                        console.error('Error publishing message:', err);
                    }
                    
                    askQuestion();
                });
            };
            
            askQuestion();

        } catch (err) {
            console.error('Error in interactive publisher:', err);
        }
    }

    /**
     * Utility function to sleep
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Wait for user input
     */
    waitForUserInput() {
        return new Promise((resolve) => {
            this.rl.question('', () => {
                resolve();
            });
        });
    }

    /**
     * Wait for interrupt signal
     */
    waitForInterrupt() {
        return new Promise((resolve) => {
            process.on('SIGINT', () => {
                console.log('\nReceived interrupt signal');
                resolve();
            });
        });
    }
}

/**
 * Main function to run examples
 */
async function main() {
    const mqttMessaging = new MQTTMessaging();
    
    while (true) {
        console.log('\nMQTT Messaging Examples');
        console.log('='.repeat(40));
        console.log('1. Simple Publisher');
        console.log('2. Simple Subscriber');
        console.log('3. Wildcard Subscriber');
        console.log('4. QoS Levels Example');
        console.log('5. Retained Messages');
        console.log('6. Will and Testament');
        console.log('7. Multiple Topics Publisher');
        console.log('8. Interactive Publisher');
        console.log('9. Exit');

        const choice = await askQuestion('Enter your choice (1-9): ');

        switch (choice.trim()) {
            case '1':
                await mqttMessaging.simplePublisherExample();
                break;
            case '2':
                await mqttMessaging.simpleSubscriberExample();
                break;
            case '3':
                await mqttMessaging.wildcardSubscriberExample();
                break;
            case '4':
                await mqttMessaging.qosLevelsExample();
                break;
            case '5':
                await mqttMessaging.retainedMessagesExample();
                break;
            case '6':
                await mqttMessaging.willAndTestamentExample();
                break;
            case '7':
                await mqttMessaging.multipleTopicsPublisherExample();
                break;
            case '8':
                await mqttMessaging.interactivePublisher();
                break;
            case '9':
                console.log('Goodbye!');
                process.exit(0);
            default:
                console.log('Invalid choice. Please try again.');
        }
    }
}

/**
 * Helper function to ask questions
 */
function askQuestion(question) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer);
        });
    });
}

// Handle process termination
process.on('SIGINT', () => {
    console.log('\nExiting...');
    process.exit(0);
});

// Run the main function
if (require.main === module) {
    main().catch(console.error);
}

module.exports = MQTTMessaging; 