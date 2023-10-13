# import the required Telegram modules
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


# define a function to handle user input for choosing a VPN protocol
async def generate_config_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    question = "Do you want to use an OpenVPN server or a WireGuard server?"
    await context.bot.send_message(chat_id, text=question, reply_markup=protocols)
