#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.
# author: M. yusuf Sarıgöz - github.com/monatis

"""
This simple Telegram bot is intended to varify ASR dataset annotations on Telegram.
You need to obtain your own API token from Bot Father on Telegram and make a few adjustments in the capitalized variables below.
"""

import logging
import os
from typing import Any, Dict, List

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

TOKEN = "<change_this_with_yours>"
BASE_DIR = '/path/to/main/directory/holding/your/dataset' # change if necessary
OPUS_DIR = os.path.join(BASE_DIR, 'opus') # Telegram expects voice files in Opus format
METADATA_FILE = os.path.join(BASE_DIR, 'metadata.csv') # file that contains annotations in ljspeech 1.1 format.
CORRECT_METADATA_FILE = os.path.join(BASE_DIR, 'correct_metadata.csv') # file to be created to write varified annotations.
START_BTN_TEXT = "Let's get started! 🚀" # change if necessary
CORRECT_BTN_TEXT = "Correct! 👍" # change if necessary
SKIP_BTN_TEXT = "Skip! ⏩" # change if necessary
HELP_TEXT = """Hello! I'm here to help you varify some voice annotations for automatic speech recognition (ASR) training).
I'll send you voice files with their transcripts. You're supposed to listen to it and varify if it is correctly annotated with a single tap of a button.
If it's not correct, then you can type the correct annotation.
If you cannot hear what is said in the voice, you may use the skip button to go to the next one.
"""


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


logger = logging.getLogger(__name__)

SHOW_HELP, ASK_TRANSCRIPT = range(2)

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[START_BTN_TEXT]]

    update.message.reply_text(
        HELP_TEXT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return SHOW_HELP


def ask_transcript(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    msg = update.message.text
    logger.info("%s: '%s'", user.first_name, msg)
    if msg != START_BTN_TEXT:
        # parse user message and correct annotation accordingly
        id = context.bot_data['cur_id']
        annotation = context.bot_data['annotations'][id]
        out_file = open(CORRECT_METADATA_FILE, 'a+', encoding='utf8')
        if msg == CORRECT_BTN_TEXT:
            out_file.write("{}|{}\n".format(annotation['file'], annotation['text']))
        elif msg == SKIP_BTN_TEXT:
            logger.debug("{} skipped by {}".format(annotation['file'], user))
        else:
            out_file.write("{}|{}\n".format(annotation['file'], msg))

        id += 1
        context.bot_data['cur_id'] = id
        out_file.close()

    send_annotation(update, context.bot_data['annotations'][context.bot_data['cur_id']])
    
    return ASK_TRANSCRIPT

def send_annotation(update: Update, annotation: Dict[str, Any]) -> None:
    reply_keyboard = [[CORRECT_BTN_TEXT, SKIP_BTN_TEXT]]
    
    with open(os.path.join(OPUS_DIR, annotation['file'] + ".opus"), 'rb') as opus_file:
        update.message.reply_voice(
            opus_file,
            filename=annotation['file'],
            caption=annotation['text'],
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
    

def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main(annotations: List[Dict[str, Any]]) -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SHOW_HELP: [MessageHandler(Filters.regex('^Hadi başlayalım!$'), ask_transcript)],
            ASK_TRANSCRIPT: [MessageHandler(Filters.regex('.*'), ask_transcript)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.bot_data['annotations'] = annotations
    dispatcher.bot_data['cur_id'] = 0

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':


    try:
        with open(METADATA_FILE, 'r', encoding='utf8') as csv_file:
            annotations = csv_file.readlines()
            annotations = [{"file": annotation.split('|')[0], "text": annotation.split('|')[1]} for annotation in annotations]
            main(annotations)

    except OSError as err:
        logger.error(f"Unable to open metadata file. Searched in {METADATA_FILE}.\n\n" + str(err))
