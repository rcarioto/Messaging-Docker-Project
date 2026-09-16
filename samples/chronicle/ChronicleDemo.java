package com.chronicle.demo;

import net.openhft.chronicle.queue.ExcerptAppender;
import net.openhft.chronicle.queue.ExcerptTailer;
import net.openhft.chronicle.queue.impl.single.SingleChronicleQueue;
import net.openhft.chronicle.queue.impl.single.SingleChronicleQueueBuilder;

/**
 * Chronicle Queue Demo
 * Chronicle Queue is a high-performance persisted messaging library
 */
public class ChronicleDemo {
    
    private static final String QUEUE_PATH = "/tmp/chronicle-demo";
    private static final int MESSAGE_COUNT = 10;
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("Starting Chronicle Queue demo...");
        
        // Create a queue
        SingleChronicleQueue queue = SingleChronicleQueueBuilder.single(QUEUE_PATH).build();
        
        // Create appender for writing messages
        ExcerptAppender appender = queue.acquireAppender();
        
        // Create tailer for reading messages
        ExcerptTailer tailer = queue.createTailer();
        
        // Write messages
        System.out.println("Writing messages to Chronicle Queue...");
        for (int i = 1; i <= MESSAGE_COUNT; i++) {
            String message = "Hello from Chronicle Queue! Message #" + i;
            appender.writeText(message);
            System.out.println("Written: " + message);
            Thread.sleep(1000);
        }
        
        // Read messages
        System.out.println("\nReading messages from Chronicle Queue...");
        int readCount = 0;
        while (readCount < MESSAGE_COUNT) {
            String message = tailer.readText();
            if (message != null) {
                System.out.println("Read: " + message);
                readCount++;
            }
            Thread.sleep(100);
        }
        
        // Close resources
        queue.close();
        System.out.println("Chronicle Queue demo completed!");
    }
} 