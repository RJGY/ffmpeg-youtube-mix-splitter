import json

from redis_pub_sub import RedisPublisher, RedisSubscriber

def process_message(message: dict) -> None:
    """Handle incoming Redis messages."""
    # Skip non-message type events (like subscribe/unsubscribe notifications)
    if message['type'] != 'message':
        return

    try:
        # Parse the JSON message data into a Python dictionary
        data = json.loads(message['data'])
        # Extract video URL and songs list from the message
        video_url = data.get('video_url')
        songs = data.get('songs')

        # Log the processed data
        print(f"Processed video: {video_url}")
        print(f"Processed songs: {songs}")

    except json.JSONDecodeError:
        # Handle malformed JSON data
        print(f"Error: Invalid JSON message received: {message['data']}")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error processing message: {str(e)}")

# Initialize a publisher to send messages to the 'mix_processing' channel
publisher = RedisPublisher(channel='mix_processing')
# Publish a message with a YouTube video URL
publisher.publish({
    "video_url": "https://www.youtube.com/watch?v=p3r7-BHAvLU"
})

# Initialize a subscriber to listen for processed results
subscriber = RedisSubscriber(channel='mix_processing_finished')
# Start listening for messages, using process_message as the callback handler
subscriber.subscribe(callback=process_message)

