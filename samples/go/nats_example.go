package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"time"

	"github.com/nats-io/nats.go"
)

// Message represents a simple message structure
type Message struct {
	ID        string    `json:"id"`
	Content   string    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
	Sender    string    `json:"sender"`
}

// NATSMessaging handles NATS connections and operations
type NATSMessaging struct {
	nc *nats.Conn
}

// NewNATSMessaging creates a new NATS messaging instance
func NewNATSMessaging(url string) (*NATSMessaging, error) {
	nc, err := nats.Connect(url)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to NATS: %v", err)
	}

	return &NATSMessaging{nc: nc}, nil
}

// Close closes the NATS connection
func (nm *NATSMessaging) Close() {
	if nm.nc != nil {
		nm.nc.Close()
	}
}

// PublishMessage publishes a message to a subject
func (nm *NATSMessaging) PublishMessage(subject, content string) error {
	msg := Message{
		ID:        fmt.Sprintf("msg-%d", time.Now().UnixNano()),
		Content:   content,
		Timestamp: time.Now(),
		Sender:    "go-client",
	}

	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %v", err)
	}

	err = nm.nc.Publish(subject, data)
	if err != nil {
		return fmt.Errorf("failed to publish message: %v", err)
	}

	fmt.Printf("Published message to '%s': %s\n", subject, content)
	return nil
}

// SubscribeToSubject subscribes to a subject and handles messages
func (nm *NATSMessaging) SubscribeToSubject(subject string) error {
	_, err := nm.nc.Subscribe(subject, func(msg *nats.Msg) {
		var message Message
		if err := json.Unmarshal(msg.Data, &message); err != nil {
			fmt.Printf("Received raw message on '%s': %s\n", subject, string(msg.Data))
		} else {
			fmt.Printf("[%s] Received: %s (from %s at %s)\n", 
				subject, message.Content, message.Sender, message.Timestamp.Format(time.RFC3339))
		}
	})

	if err != nil {
		return fmt.Errorf("failed to subscribe to subject: %v", err)
	}

	fmt.Printf("Subscribed to subject: %s\n", subject)
	return nil
}

// SubscribeWithQueueGroup subscribes to a subject with a queue group for load balancing
func (nm *NATSMessaging) SubscribeWithQueueGroup(subject, queueGroup string) error {
	_, err := nm.nc.QueueSubscribe(subject, queueGroup, func(msg *nats.Msg) {
		var message Message
		if err := json.Unmarshal(msg.Data, &message); err != nil {
			fmt.Printf("[%s] Received raw message: %s\n", queueGroup, string(msg.Data))
		} else {
			fmt.Printf("[%s] Received: %s (from %s)\n", queueGroup, message.Content, message.Sender)
		}
	})

	if err != nil {
		return fmt.Errorf("failed to subscribe with queue group: %v", err)
	}

	fmt.Printf("Subscribed to subject '%s' with queue group '%s'\n", subject, queueGroup)
	return nil
}

// RequestReply sends a request and waits for a response
func (nm *NATSMessaging) RequestReply(subject, request string, timeout time.Duration) error {
	req := Message{
		ID:        fmt.Sprintf("req-%d", time.Now().UnixNano()),
		Content:   request,
		Timestamp: time.Now(),
		Sender:    "go-client",
	}

	data, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %v", err)
	}

	response, err := nm.nc.Request(subject, data, timeout)
	if err != nil {
		return fmt.Errorf("failed to send request: %v", err)
	}

	var resp Message
	if err := json.Unmarshal(response.Data, &resp); err != nil {
		fmt.Printf("Received raw response: %s\n", string(response.Data))
	} else {
		fmt.Printf("Response: %s (from %s)\n", resp.Content, resp.Sender)
	}

	return nil
}

// ReplyToRequests handles incoming requests and sends responses
func (nm *NATSMessaging) ReplyToRequests(subject string) error {
	_, err := nm.nc.Subscribe(subject, func(msg *nats.Msg) {
		var request Message
		if err := json.Unmarshal(msg.Data, &request); err != nil {
			fmt.Printf("Received invalid request: %s\n", string(msg.Data))
			return
		}

		fmt.Printf("Received request: %s\n", request.Content)

		// Process the request and create a response
		response := Message{
			ID:        fmt.Sprintf("resp-%d", time.Now().UnixNano()),
			Content:   fmt.Sprintf("Processed: %s", request.Content),
			Timestamp: time.Now(),
			Sender:    "go-server",
		}

		data, err := json.Marshal(response)
		if err != nil {
			fmt.Printf("Failed to marshal response: %v\n", err)
			return
		}

		// Send the response
		err = msg.Respond(data)
		if err != nil {
			fmt.Printf("Failed to send response: %v\n", err)
		} else {
			fmt.Printf("Sent response: %s\n", response.Content)
		}
	})

	if err != nil {
		return fmt.Errorf("failed to subscribe for requests: %v", err)
	}

	fmt.Printf("Listening for requests on subject: %s\n", subject)
	return nil
}

// PublishToStream publishes messages to a JetStream stream
func (nm *NATSMessaging) PublishToStream(streamName, subject, content string) error {
	js, err := nm.nc.JetStream()
	if err != nil {
		return fmt.Errorf("failed to get JetStream context: %v", err)
	}

	msg := Message{
		ID:        fmt.Sprintf("stream-msg-%d", time.Now().UnixNano()),
		Content:   content,
		Timestamp: time.Now(),
		Sender:    "go-stream-producer",
	}

	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %v", err)
	}

	ack, err := js.Publish(subject, data)
	if err != nil {
		return fmt.Errorf("failed to publish to stream: %v", err)
	}

	fmt.Printf("Published to stream '%s' (subject: %s): %s (ack: %d)\n", 
		streamName, subject, content, ack.Sequence)
	return nil
}

// SubscribeToStream subscribes to messages from a JetStream stream
func (nm *NATSMessaging) SubscribeToStream(streamName, subject, consumerName string) error {
	js, err := nm.nc.JetStream()
	if err != nil {
		return fmt.Errorf("failed to get JetStream context: %v", err)
	}

	sub, err := js.Subscribe(subject, func(msg *nats.Msg) {
		var message Message
		if err := json.Unmarshal(msg.Data, &message); err != nil {
			fmt.Printf("[%s] Received raw message: %s\n", consumerName, string(msg.Data))
		} else {
			fmt.Printf("[%s] Received: %s (from %s)\n", consumerName, message.Content, message.Sender)
		}

		// Acknowledge the message
		msg.Ack()
	}, nats.Durable(consumerName))

	if err != nil {
		return fmt.Errorf("failed to subscribe to stream: %v", err)
	}

	fmt.Printf("Subscribed to stream '%s' with consumer '%s' on subject '%s'\n", 
		streamName, consumerName, subject)

	// Keep the subscription alive
	go func() {
		<-sub.Closed
		fmt.Printf("Subscription to stream '%s' closed\n", streamName)
	}()

	return nil
}

// CreateStream creates a new JetStream stream
func (nm *NATSMessaging) CreateStream(streamName string, subjects []string) error {
	js, err := nm.nc.JetStream()
	if err != nil {
		return fmt.Errorf("failed to get JetStream context: %v", err)
	}

	stream, err := js.AddStream(&nats.StreamConfig{
		Name:     streamName,
		Subjects: subjects,
		Storage:  nats.FileStorage,
	})

	if err != nil {
		return fmt.Errorf("failed to create stream: %v", err)
	}

	fmt.Printf("Created stream '%s' with %d subjects\n", stream.Config.Name, len(stream.Config.Subjects))
	return nil
}

func main() {
	// Connect to NATS
	nm, err := NewNATSMessaging("nats://localhost:4222")
	if err != nil {
		log.Fatal(err)
	}
	defer nm.Close()

	// Set up signal handling for graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt)

	for {
		fmt.Println("\nNATS Messaging Examples")
		fmt.Println(strings.Repeat("=", 40))
		fmt.Println("1. Simple Publisher")
		fmt.Println("2. Simple Subscriber")
		fmt.Println("3. Queue Group Subscriber")
		fmt.Println("4. Request-Reply Client")
		fmt.Println("5. Request-Reply Server")
		fmt.Println("6. JetStream Publisher")
		fmt.Println("7. JetStream Subscriber")
		fmt.Println("8. Create JetStream")
		fmt.Println("9. Exit")

		fmt.Print("Enter your choice (1-9): ")
		var choice string
		fmt.Scanln(&choice)

		switch choice {
		case "1":
			runSimplePublisher(nm)
		case "2":
			runSimpleSubscriber(nm)
		case "3":
			runQueueGroupSubscriber(nm)
		case "4":
			runRequestReplyClient(nm)
		case "5":
			runRequestReplyServer(nm)
		case "6":
			runJetStreamPublisher(nm)
		case "7":
			runJetStreamSubscriber(nm)
		case "8":
			runCreateJetStream(nm)
		case "9":
			fmt.Println("Goodbye!")
			return
		default:
			fmt.Println("Invalid choice. Please try again.")
		}

		// Check for interrupt signal
		select {
		case <-sigChan:
			fmt.Println("\nReceived interrupt signal. Exiting...")
			return
		default:
			// Continue
		}
	}
}

func runSimplePublisher(nm *NATSMessaging) {
	fmt.Println("\n=== Simple Publisher Example ===")
	
	subjects := []string{"news", "weather", "sports"}
	messages := []string{
		"Breaking news: New technology breakthrough!",
		"Weather update: Sunny with clear skies",
		"Sports update: Team wins championship!",
	}

	for i, message := range messages {
		subject := subjects[i%len(subjects)]
		err := nm.PublishMessage(subject, message)
		if err != nil {
			fmt.Printf("Error publishing message: %v\n", err)
		}
		time.Sleep(1 * time.Second)
	}
}

func runSimpleSubscriber(nm *NATSMessaging) {
	fmt.Println("\n=== Simple Subscriber Example ===")
	
	subject := "news"
	err := nm.SubscribeToSubject(subject)
	if err != nil {
		fmt.Printf("Error subscribing: %v\n", err)
		return
	}

	fmt.Printf("Listening for messages on '%s'. Press Ctrl+C to stop...\n", subject)
	
	// Keep the program running
	select {}
}

func runQueueGroupSubscriber(nm *NATSMessaging) {
	fmt.Println("\n=== Queue Group Subscriber Example ===")
	
	subject := "weather"
	queueGroup := "weather-processors"
	
	err := nm.SubscribeWithQueueGroup(subject, queueGroup)
	if err != nil {
		fmt.Printf("Error subscribing with queue group: %v\n", err)
		return
	}

	fmt.Printf("Listening for messages on '%s' with queue group '%s'. Press Ctrl+C to stop...\n", subject, queueGroup)
	
	// Keep the program running
	select {}
}

func runRequestReplyClient(nm *NATSMessaging) {
	fmt.Println("\n=== Request-Reply Client Example ===")
	
	subject := "service.request"
	request := "Calculate fibonacci(10)"
	
	err := nm.RequestReply(subject, request, 5*time.Second)
	if err != nil {
		fmt.Printf("Error in request-reply: %v\n", err)
	}
}

func runRequestReplyServer(nm *NATSMessaging) {
	fmt.Println("\n=== Request-Reply Server Example ===")
	
	subject := "service.request"
	
	err := nm.ReplyToRequests(subject)
	if err != nil {
		fmt.Printf("Error setting up request handler: %v\n", err)
		return
	}

	fmt.Printf("Server listening for requests on '%s'. Press Ctrl+C to stop...\n", subject)
	
	// Keep the program running
	select {}
}

func runJetStreamPublisher(nm *NATSMessaging) {
	fmt.Println("\n=== JetStream Publisher Example ===")
	
	streamName := "test-stream"
	subject := "test.messages"
	
	for i := 1; i <= 5; i++ {
		content := fmt.Sprintf("JetStream message %d at %s", i, time.Now().Format(time.RFC3339))
		err := nm.PublishToStream(streamName, subject, content)
		if err != nil {
			fmt.Printf("Error publishing to stream: %v\n", err)
		}
		time.Sleep(1 * time.Second)
	}
}

func runJetStreamSubscriber(nm *NATSMessaging) {
	fmt.Println("\n=== JetStream Subscriber Example ===")
	
	streamName := "test-stream"
	subject := "test.messages"
	consumerName := "test-consumer"
	
	err := nm.SubscribeToStream(streamName, subject, consumerName)
	if err != nil {
		fmt.Printf("Error subscribing to stream: %v\n", err)
		return
	}

	fmt.Printf("Listening for messages from stream '%s'. Press Ctrl+C to stop...\n", streamName)
	
	// Keep the program running
	select {}
}

func runCreateJetStream(nm *NATSMessaging) {
	fmt.Println("\n=== Create JetStream Example ===")
	
	streamName := "test-stream"
	subjects := []string{"test.*"}
	
	err := nm.CreateStream(streamName, subjects)
	if err != nil {
		fmt.Printf("Error creating stream: %v\n", err)
	}
} 