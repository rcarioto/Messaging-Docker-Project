#!/usr/bin/env python3
"""
Fast DDS Demo Example
Fast DDS is a high-performance DDS implementation
"""

import fastdds
import time
import threading

class FastDDSDemo:
    def __init__(self, participant_name="demo-participant"):
        self.participant_name = participant_name
        self.participant = None
        self.running = False
        
    def start(self):
        """Start the DDS participant"""
        try:
            # Create participant QoS
            participant_qos = fastdds.ParticipantQos()
            
            # Create domain participant
            self.participant = fastdds.DomainParticipantFactory.get_instance().create_participant(
                0, participant_qos
            )
            
            if self.participant is None:
                print("Failed to create DDS participant")
                return False
                
            self.running = True
            print(f"Fast DDS participant '{self.participant_name}' started")
            return True
            
        except Exception as e:
            print(f"Error starting DDS participant: {e}")
            return False
            
    def stop(self):
        """Stop the DDS participant"""
        if self.participant:
            fastdds.DomainParticipantFactory.get_instance().delete_participant(self.participant)
            self.participant = None
        self.running = False
        print(f"Fast DDS participant '{self.participant_name}' stopped")
        
    def run_demo(self, duration=30):
        """Run the demo for a specified duration"""
        if not self.start():
            return
            
        # Simulate DDS operations
        message_count = 0
        start_time = time.time()
        
        while time.time() - start_time < duration and self.running:
            message_count += 1
            print(f"DDS demo running... Message #{message_count}")
            time.sleep(5)
            
        self.stop()

def main():
    # Create and run demo
    demo = FastDDSDemo("demo-participant-1")
    
    try:
        print("Starting Fast DDS demo (30 seconds)...")
        demo.run_demo(30)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        demo.stop()
    except Exception as e:
        print(f"Demo error: {e}")
        demo.stop()

if __name__ == "__main__":
    main() 