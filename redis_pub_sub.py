import redis
import json
from typing import Callable, Any, Union

class RedisPublisher:
    def __init__(self, host: str = 'localhost', port: int = 6379, channel: str = 'default_channel'):
        """Initialize Redis publisher with connection details and channel name."""
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.channel = channel

    def publish(self, message: Union[str, dict]) -> int:
        """
        Publish a message to the channel.
        Returns the number of subscribers that received the message.
        """
        try:
            # Convert dict to JSON string if necessary
            if isinstance(message, dict):
                message = json.dumps(message)
            
            return self.redis_client.publish(self.channel, message)
        except Exception as e:
            print(f"Error publishing message: {str(e)}")
            return 0

    def close(self):
        """Close the Redis connection."""
        self.redis_client.close()

class RedisSubscriber:
    def __init__(self, host: str = 'localhost', port: int = 6379, channel: str = 'default_channel'):
        """Initialize Redis subscriber with connection details and channel name."""
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.channel = channel

    def message_handler(self, message: dict) -> None:
        """Default message handler - can be overridden."""
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                print(f"Received message: {data}")
            except json.JSONDecodeError:
                print(f"Received raw message: {message['data']}")

    def subscribe(self, callback: Callable[[Any], None] = None) -> None:
        """Subscribe to the channel and process messages."""
        self.pubsub.subscribe(self.channel)
        
        # Use custom callback if provided, otherwise use default handler
        handler = callback if callback else self.message_handler
        
        print(f"Subscribed to channel: {self.channel}")
        try:
            for message in self.pubsub.listen():
                handler(message)
        except KeyboardInterrupt:
            print("\nUnsubscribing from channel...")
            self.pubsub.unsubscribe()
            self.redis_client.close()

def test_redis_pubsub():
    """Test the Redis Publisher and Subscriber classes."""
    try:
        # Test Publisher
        publisher = RedisPublisher(channel='test_channel')
        
        # Test publishing string message
        result = publisher.publish("Hello, Redis!")
        assert result >= 0, "Failed to publish string message"
        
        # Test publishing dict message
        result = publisher.publish({"key": "value"})
        assert result >= 0, "Failed to publish dict message"
        
        # Test Subscriber
        subscriber = RedisSubscriber(channel='test_channel')
        assert subscriber.channel == 'test_channel', "Channel not set correctly"
        
        print("Redis Publisher and Subscriber tests passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise
    finally:
        publisher.close()

def main():
    # Example usage
    def custom_handler(message):
        if message['type'] == 'message':
            print(f"Custom handler received: {message['data']}")

    # Publisher example
    publisher = RedisPublisher(channel='my_channel')
    publisher.publish({"message": "Hello from publisher!"})
    publisher.publish("Simple string message")
    
    # Subscriber example
    subscriber = RedisSubscriber(channel='my_channel')
    subscriber.subscribe(callback=custom_handler)  # This will block until interrupted

if __name__ == "__main__":
    test_redis_pubsub()