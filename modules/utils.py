# import the required modules
import asyncio  # for asynchronous programming
import json  # for working with JSON data
from functools import wraps  # for using function decorators
from modules.language_functions import *

# import the required Telegram modules
from telegram.constants import ChatAction
from telegram.ext import ContextTypes


# define the send_action decorator
def send_action(action, delay=1):
    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )
            await asyncio.sleep(delay)  # wait for the specified delay time
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator


# set the aliases with custom delays
send_upload_document_action = send_action(ChatAction.UPLOAD_DOCUMENT)
send_typing_action = send_action(
    ChatAction.TYPING, delay=1
)  # change the delay time as needed
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)


# define a function to display a message with streaming text
@send_typing_action
async def smooth_streaming_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, delimiter: str
):
    # get the user's language preference
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

        # split the message into sentences using the custom delimiter
        sentences = strings[message].split(delimiter)

        # send the first sentence as a new message
        text = sentences[0]
        message = await update.message.reply_text(text)

        # loop through each sentence and gradually build up the message, editing the original message with a delay in
        # between
        for sentence in sentences[1:]:
            text += delimiter + sentence
            await message.edit_text(text)
            await asyncio.sleep(0.05)
