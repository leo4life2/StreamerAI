import logging
import argparse
from StreamerAI.streamchat.streamChatHandler import StreamChatHandler

# Set up a logger for this module.
logger = logging.getLogger("StreamerAI.FakeHandler")

# Define command-line arguments.
parser = argparse.ArgumentParser(description="Fake chat handler for testing.")
parser.add_argument('--room_id', type=str, required=True, help='ID of the chat room.')
args = parser.parse_args()

# The ID of the room in the chat service.
room_id = args.room_id

# Instantiating StreamChatHandler
streamChatHandler = StreamChatHandler(room_id, "FAKE")

# A fake username to be used for testing.
FAKE_USERNAME = "大脸猫"

def main():
    """
    The main function that runs an infinite loop, prompting the user to insert a 
    fake stream comment and then sending that comment to the chat handler.
    """
    while True:
        # Prompt the user to input a new fake stream comment.
        new_comment = input("Insert stream comment: ")
        
        # Handle the new comment using the StreamChatHandler.
        streamChatHandler.on_comment(FAKE_USERNAME, new_comment)