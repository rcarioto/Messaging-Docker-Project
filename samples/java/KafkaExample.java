import org.apache.kafka.clients.producer.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.common.TopicPartition;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

/**
 * Apache Kafka Messaging Examples
 * Demonstrates producer and consumer patterns using Kafka
 */
public class KafkaExample {
    
    private static final String BOOTSTRAP_SERVERS = "localhost:9092";
    private static final String TOPIC_NAME = "test-topic";
    private static final String GROUP_ID = "test-group";
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        while (true) {
            System.out.println("\nApache Kafka Messaging Examples");
            System.out.println("=" * 40);
            System.out.println("1. Simple Producer");
            System.out.println("2. Simple Consumer");
            System.out.println("3. Producer with Callback");
            System.out.println("4. Consumer with Manual Offset Control");
            System.out.println("5. Producer with Partitioning");
            System.out.println("6. Consumer with Multiple Topics");
            System.out.println("7. Exit");
            
            System.out.print("Enter your choice (1-7): ");
            String choice = scanner.nextLine().trim();
            
            switch (choice) {
                case "1":
                    simpleProducerExample();
                    break;
                case "2":
                    simpleConsumerExample();
                    break;
                case "3":
                    producerWithCallbackExample();
                    break;
                case "4":
                    consumerWithManualOffsetExample();
                    break;
                case "5":
                    producerWithPartitioningExample();
                    break;
                case "6":
                    consumerWithMultipleTopicsExample();
                    break;
                case "7":
                    System.out.println("Goodbye!");
                    scanner.close();
                    return;
                default:
                    System.out.println("Invalid choice. Please try again.");
            }
        }
    }
    
    /**
     * Simple Kafka Producer Example
     */
    public static void simpleProducerExample() {
        System.out.println("\n=== Simple Producer Example ===");
        
        // Producer configuration
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 1);
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 33554432);
        
        try (Producer<String, String> producer = new KafkaProducer<>(props)) {
            
            for (int i = 0; i < 10; i++) {
                String key = "key-" + i;
                String value = "Message " + i + " from Java producer at " + new Date();
                
                ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC_NAME, key, value);
                
                // Send message synchronously
                Future<RecordMetadata> future = producer.send(record);
                RecordMetadata metadata = future.get();
                
                System.out.printf("Sent message: key=%s, value=%s, partition=%d, offset=%d%n",
                        key, value, metadata.partition(), metadata.offset());
                
                Thread.sleep(1000); // Wait 1 second between messages
            }
            
        } catch (InterruptedException | ExecutionException e) {
            System.err.println("Error in producer: " + e.getMessage());
        }
    }
    
    /**
     * Simple Kafka Consumer Example
     */
    public static void simpleConsumerExample() {
        System.out.println("\n=== Simple Consumer Example ===");
        
        // Consumer configuration
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP_ID);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, "1000");
        
        try (Consumer<String, String> consumer = new KafkaConsumer<>(props)) {
            
            // Subscribe to topic
            consumer.subscribe(Arrays.asList(TOPIC_NAME));
            System.out.println("Subscribed to topic: " + TOPIC_NAME);
            
            // Poll for messages
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("Received message: topic=%s, partition=%d, offset=%d, key=%s, value=%s%n",
                            record.topic(), record.partition(), record.offset(), record.key(), record.value());
                }
                
                // Check for exit condition (you can modify this)
                if (records.count() > 0) {
                    System.out.println("Press Ctrl+C to stop consumer...");
                }
            }
            
        } catch (Exception e) {
            System.err.println("Error in consumer: " + e.getMessage());
        }
    }
    
    /**
     * Producer with Callback Example
     */
    public static void producerWithCallbackExample() {
        System.out.println("\n=== Producer with Callback Example ===");
        
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        
        try (Producer<String, String> producer = new KafkaProducer<>(props)) {
            
            for (int i = 0; i < 5; i++) {
                String key = "callback-key-" + i;
                String value = "Callback message " + i + " at " + new Date();
                
                ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC_NAME, key, value);
                
                // Send message with callback
                producer.send(record, new Callback() {
                    @Override
                    public void onCompletion(RecordMetadata metadata, Exception exception) {
                        if (exception != null) {
                            System.err.println("Error sending message: " + exception.getMessage());
                        } else {
                            System.out.printf("Message sent successfully: topic=%s, partition=%d, offset=%d%n",
                                    metadata.topic(), metadata.partition(), metadata.offset());
                        }
                    }
                });
                
                Thread.sleep(1000);
            }
            
            // Flush to ensure all messages are sent
            producer.flush();
            System.out.println("All messages sent with callbacks");
            
        } catch (InterruptedException e) {
            System.err.println("Error in producer with callback: " + e.getMessage());
        }
    }
    
    /**
     * Consumer with Manual Offset Control Example
     */
    public static void consumerWithManualOffsetExample() {
        System.out.println("\n=== Consumer with Manual Offset Control ===");
        
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP_ID + "-manual");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");
        
        try (Consumer<String, String> consumer = new KafkaConsumer<>(props)) {
            
            consumer.subscribe(Arrays.asList(TOPIC_NAME));
            System.out.println("Subscribed to topic with manual offset control: " + TOPIC_NAME);
            
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("Processing message: topic=%s, partition=%d, offset=%d, key=%s, value=%s%n",
                            record.topic(), record.partition(), record.offset(), record.key(), record.value());
                    
                    // Process the message here
                    // ...
                    
                    // Manually commit offset for this specific partition and offset
                    Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
                    offsets.put(new TopicPartition(record.topic(), record.partition()),
                            new OffsetAndMetadata(record.offset() + 1));
                    consumer.commitSync(offsets);
                    
                    System.out.println("Committed offset: " + (record.offset() + 1));
                }
            }
            
        } catch (Exception e) {
            System.err.println("Error in manual offset consumer: " + e.getMessage());
        }
    }
    
    /**
     * Producer with Partitioning Example
     */
    public static void producerWithPartitioningExample() {
        System.out.println("\n=== Producer with Partitioning Example ===");
        
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, "org.apache.kafka.clients.producer.internals.DefaultPartitioner");
        
        try (Producer<String, String> producer = new KafkaProducer<>(props)) {
            
            // Send messages with different keys to demonstrate partitioning
            String[] keys = {"user1", "user2", "user3", "user1", "user2"};
            
            for (int i = 0; i < keys.length; i++) {
                String key = keys[i];
                String value = "Partitioned message " + i + " for " + key + " at " + new Date();
                
                ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC_NAME, key, value);
                
                Future<RecordMetadata> future = producer.send(record);
                RecordMetadata metadata = future.get();
                
                System.out.printf("Sent message: key=%s, value=%s, partition=%d, offset=%d%n",
                        key, value, metadata.partition(), metadata.offset());
                
                Thread.sleep(1000);
            }
            
        } catch (InterruptedException | ExecutionException e) {
            System.err.println("Error in partitioning producer: " + e.getMessage());
        }
    }
    
    /**
     * Consumer with Multiple Topics Example
     */
    public static void consumerWithMultipleTopicsExample() {
        System.out.println("\n=== Consumer with Multiple Topics Example ===");
        
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, GROUP_ID + "-multi");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        
        try (Consumer<String, String> consumer = new KafkaConsumer<>(props)) {
            
            // Subscribe to multiple topics
            List<String> topics = Arrays.asList(TOPIC_NAME, "topic2", "topic3");
            consumer.subscribe(topics);
            System.out.println("Subscribed to topics: " + topics);
            
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("Received from %s: partition=%d, offset=%d, key=%s, value=%s%n",
                            record.topic(), record.partition(), record.offset(), record.key(), record.value());
                }
            }
            
        } catch (Exception e) {
            System.err.println("Error in multi-topic consumer: " + e.getMessage());
        }
    }
} 