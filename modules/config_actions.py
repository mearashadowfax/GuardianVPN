# import the required modules
import json  # for working with JSON data
from modules.language_functions import *

# import the required Telegram modules
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


# define a function to handle user input for choosing a VPN protocol
async def generate_config_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

    # create InlineKeyboardMarkup with buttons for the user to select OpenVPN or Wireguard
    buttons = [
        [
            InlineKeyboardButton(text="OpenVPN", callback_data="openvpn"),
            InlineKeyboardButton(text="WireGuard", callback_data="wireguard"),
        ],
        [InlineKeyboardButton("Help me choose", callback_data="suggest")],
    ]
    protocols = InlineKeyboardMarkup(buttons)

    # ask the user whether they want to use OpenVPN or Wireguard
    chat_id = update.message.chat_id
    question = strings["question"]
    await context.bot.send_message(chat_id, text=question, reply_markup=protocols)
