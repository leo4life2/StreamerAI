import cv2
import numpy as np
import logging

class StreamDisplay:

    def __init__(self):
        self.window_name = "StreamDisplay"
        self.x = 300
        self.y = 300

    def setup_display(self):

        # Create a blank image with a white background
        image = 255 * np.ones((200, 400, 3), dtype=np.uint8)

        # Set the text parameters
        text = "TEST WINDOW WILL DISPLAY HERE"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (0, 0, 0)  # Black color
        thickness = 1

        # Determine the text size
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

        # Calculate the position to center the text
        x = int((image.shape[1] - text_width) / 2)
        y = int((image.shape[0] + text_height) / 2)

        # Put the text on the image
        cv2.putText(image, text, (x, y), font, font_scale, font_color, thickness)

        # Display the image
        cv2.imshow(self.window_name, image)

        # Move the image to the preset position
        cv2.moveWindow(self.window_name, self.x, self.y)
        logging.info(f"window {self.window_name} is being displayed at: {cv2.getWindowImageRect(self.window_name)}")

        # Wait for user to ack
        cv2.waitKey(10000)

        cv2.destroyAllWindows()
        
    def display_asset(self, asset):

        # Grab image from bytes
        image_array = np.frombuffer(asset.asset, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Set up image display
        cv2.imshow(self.window_name, image)

        # Move window to same preset position
        cv2.moveWindow(self.window_name, self.x, self.y)
        logging.info(f"window {self.window_name} is being displayed at: {cv2.getWindowImageRect(self.window_name)}")

        # Display
        cv2.waitKey(1)

    def __del__(self):
        cv2.destroyAllWindows()
