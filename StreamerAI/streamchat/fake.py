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
    current_user_name = FAKE_USERNAME

    while True:
        # Prompt the user to input a new fake stream comment.
        user_input = input("type 'c' to insert a comment, 'n' to change the current user name: ")
        if user_input == 'c':
            new_comment = input("insert stream comment: ")
            # Handle the new comment using the StreamChatHandler.
            streamChatHandler.on_comment(current_user_name, new_comment)
        elif user_input == 'n':
            new_user = input("new username: ")
            streamChatHandler.on_join(new_user)
            current_user_name = new_user
