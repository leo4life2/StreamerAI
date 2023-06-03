import atexit
import logging
import subprocess
import time
import os
import argparse

from StreamerAI.gpt.chains import Chains
from StreamerAI.database.database import Stream, Comment, Product, Asset, Persona
from StreamerAI.settings import QUESTION_ANSWERING_SCRIPT_PLACEHOLDER, ASSET_DISPLAY_SCRIPT_PLACEHOLDER
from StreamerAI.streaming.tts import TextToSpeech
from StreamerAI.streaming.streamdisplay import StreamDisplay

logger = logging.getLogger("StreamerAI")

class StreamerAI:
    """
    A class that represents a streamer AI, which can fetch scripts, answer comments, and handle text-to-speech.
    """
    
    def __init__(self, room_id, live=False, disable_script=False, voice_type=None, voice_style=None, persona=None):
        """
        Initializes a new StreamerAI instance.

        Args:
            room_id (str): The ID of the room to connect to.
            live (bool): Whether to fetch comments live.
            voice_type (str): The type of voice to use for text-to-speech.
            voice_style (str): The name of the style to use for text-to-speech.
        """
        self.room_id = room_id
        self.live = live
        self.disable_script = disable_script
        self.tts_service = TextToSpeech(voice_type=voice_type, style_name=voice_style)
        self.subprocesses = []
        
        # MARK: initialize TTS
        if voice_type and voice_style:
            self.tts_service = TextToSpeech(voice_type=voice_type, style_name=voice_style)
        elif voice_type:
            self.tts_service = TextToSpeech(voice_type=voice_type)
        else:
            self.tts_service = TextToSpeech()

        # MARK: initialize Stream
        stream = Stream.select().where(Stream.identifier == room_id).first()
        if not stream:
            stream = Stream.create(identifier=room_id, cursor=None)
        self.stream = stream

        # MARK: initialize Products list
        self.products = Product.select()[:]

        # MARK: initialize Persona
        self.persona = Persona.select().where(Persona.name == 'Default').first()
        if persona:
            resolved_persona = Persona.select().where(Persona.name == persona).first()
            if resolved_persona:
                self.persona = resolved_persona
            else:
                logger.error(f"persona {persona} supplied as argument, but not found in database - falling back to default")
        Persona.update(current=False).execute()
        self.persona.current = True
        self.persona.save()

        # MARK: scheduled messages
        self.last_scheduled_message_time = time.time()
        self.scheduled_message_interval = 300 # every 5 minutes

        # MARK: initialize display
        self.streamdisplay = StreamDisplay()
        self.streamdisplay.setup_display()

        # MARK: initialize stream comments subprocess
        atexit.register(self.terminate_subprocesses)
        if self.live:
            self.start_polling_for_comments()

        logger.info("StreamerAI initialized!")

    def start_polling_for_comments(self):
        """
        Starts polling for new comments.
        """
        logger.info("StreamerAI is live, starting subprocess to poll for comments")
        streamchat_filename = os.path.join(os.path.dirname(__file__), "streamchat.py")
        comments_command = command = ['python', streamchat_filename, self.room_id]
        process = subprocess.Popen(comments_command, stdout=subprocess.PIPE)
        self.subprocesses.append(process)

    def terminate_subprocesses(self):
        """
        Terminates all subprocesses created by this StreamerAI instance.
        """
        logger.info("atexit invoked terminate_subprocesses, terminating: {}".format(self.subprocesses))
        for subprocess in self.subprocesses:
            subprocess.terminate()

    def process_media_asset(self, asset_name, current_product):
        asset = Asset.select().where(Asset.product == current_product, Asset.name == asset_name).first()
        logger.info(f"process_media_asset fetched asset: {asset} for asset_name: {asset_name}")
        if asset:
            self.streamdisplay.display_asset(asset)
            
    def process_comments(self, current_product):
        """
        Processes a list of comments.
        """
        comment_results = Comment.select().where(Comment.stream == self.stream, Comment.read == False)[:]
        for comment in comment_results:

            username = comment.username
            text = comment.comment
            response = comment.reply

            logger.info(
                f"User: {username}"
                f"Comment: {text}\n"
                f"Response: {response}\n"
            )
            
            try:
                time_taken = self.tts_service.tts(response)
                logger.debug(f"TTS server took: {time_taken} seconds")
            except Exception as e:
                logger.error(f"TTS Error: {e}")
                continue

            comment.read = True
            comment.save()

    def should_handle_scheduled_message(self):
        time_delta = time.time() - self.last_scheduled_message_time
        return time_delta > self.scheduled_message_interval

    def should_handle_comments_for_paragraph(self, paragraph):
        return paragraph == QUESTION_ANSWERING_SCRIPT_PLACEHOLDER or self.disable_script
    
    def should_display_asset_for_paragraph(self, paragraph):
        return "{{{" in paragraph and "}}}" in paragraph
    
    def process_scheduled_message(self):
        chain = Chains.create_chain(prompt_type="scheduled")
        response = chain.predict(
            human_input='',
            product_context='',
            other_available_products='',
            audience_name=''
        )
        logger.info(f"processing scheduled message response: {response}")
        if (response):
            self.tts_service.tts(response)

    def process_paragraph(self, paragraph, current_product):
        """
        Processes a single paragraph in the product's script

        The script paragraph could represent:
        1) A simple paragraph meant to be read out loud via TTS
        2) "{question}" - denoting that it's time to pause and answer questions
        3) "{{{assetname}}} - denoting that the image or video with name should start playing
        """
        if self.should_handle_scheduled_message():
            self.process_scheduled_message()

        logger.info(f"processing paragraph: {paragraph}")
        if self.should_handle_comments_for_paragraph(paragraph):
            self.process_comments(current_product)
            time.sleep(1)
        elif self.should_display_asset_for_paragraph(paragraph):
            assetname = paragraph.replace("{{{", "").replace("}}}", "")
            self.process_media_asset(assetname, current_product)
        else:
            time_taken = self.tts_service.tts(paragraph)
            logger.info(f"Time taken for TTS request: {time_taken} seconds")

    def process_product(self, current_product):
        """
        Processes a single product
        """
        current_product.current = True
        current_product.save()

        script_paragraphs = [paragraph for paragraph in current_product.script.split("\n") if paragraph != '']
        for paragraph in script_paragraphs:
            self.process_paragraph(paragraph, current_product)

        # clear out any pending questions before switching to next product
        self.process_comments(current_product)

        current_product.current = False
        current_product.save()

    def run(self):
        """
        Runs the StreamerAI instance.
        """
        # reset all products to not current, in case this script was killed during execution
        Product.update(current=False).execute()
        while True:
            for product in self.products:
                self.process_product(product)
            logger.info("StreamerAI finished all products - restarting from beginning")
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--room_id', type=str, required=True, help='Room ID for the product assistant')
    parser.add_argument('--voice_type', type=str, help='Voice type for text-to-speech')
    parser.add_argument('--voice_style', type=str, help='Voice style for text-to-speech')
    parser.add_argument('--live', action='store_true', help='Enable live mode for streaming comments')
    parser.add_argument('--disable_script', action='store_true', help='Disable script reading mode')
    parser.add_argument('--persona', type=str, help='Select a persona to use')

    args = parser.parse_args()

    product_assistant = StreamerAI(
        room_id=args.room_id,
        live=args.live,
        disable_script=args.disable_script,
        voice_type=args.voice_type,
        voice_style=args.voice_style,
        persona=args.persona
    )

    product_assistant.run()