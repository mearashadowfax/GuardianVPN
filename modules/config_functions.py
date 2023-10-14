# import the required modules
import subprocess  # for running shell commands
import os  # for working with the operating system
import datetime  # for getting the current date/time
import json  # for working with JSON data
import time  # for working with time-related operations
import pexpect  # for interacting with command line prompts
import logging  # for logging to help debug and troubleshoot the program
from modules.utils import *
from modules.language_functions import *
from modules.config_actions import *

# import the file paths
from config import OVPN_FILE_PATH, WG_FILE_PATH, QR_CODE_PATH

# import the required Telegram modules
from telegram.constants import ChatAction
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

    # create InlineKeyboardMarkup with two buttons for the user to select product
    buttons = [
        [InlineKeyboardButton(text="1 Week - $1", callback_data="product_a")],
        [InlineKeyboardButton(text="1 Month - $3", callback_data="product_b")],
    ]

    products = InlineKeyboardMarkup(buttons)

    # send message to the user with the two products to choose from
    chat_id = update.message.chat_id
    description = strings["description"]
    await context.bot.send_message(chat_id, description, reply_markup=products)


# callback function after choosing the VPN protocol
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

    # extract the callback query and chat id from the update object
    query = update.callback_query
    choice = query.data
    chat_id = query.message.chat_id

    # get the selected plan and duration days from the user data
    user_data = context.user_data
    selected_plan = user_data.get("selected_plan")

    if choice == "suggest":
        # suggest the VPN protocol to use
        differences = strings["differences"]
        await context.bot.send_message(chat_id, differences)

    else:
        # call the corresponding handler function
        handler_map = {"openvpn": openvpn_callback, "wireguard": wireguard_callback}
        handler = handler_map.get(choice)
        await handler(update, context)

        # send a message to the user confirming the duration of their plan
        duration_message = (
            f"Your GuardianVPN service will be active for {selected_plan}."
        )
        await context.bot.send_message(chat_id, duration_message)
        # delete the inline keyboard to prevent the user from clicking again
        await context.bot.delete_message(chat_id, query.message.message_id)


# send a typing indicator in the chat
@send_upload_document_action
# generate client config file for OpenVPN
async def openvpn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

    # get the duration days from the user data
    duration_days = context.user_data.get("duration_days")

    # extract the callback query and chat id from the update object
    query = update.callback_query
    chat_id = query.message.chat_id

    # get the user ID from the Telegram message
    user_id = query.from_user.id
    # generate a unique client name based on the user ID
    client_name = f"user_{user_id}"
    # note: this command requires root privileges
    return_code = subprocess.run(
        [
            "pivpn",
            "ovpn",
            "add",
            "nopass",
            "-n",
            client_name,
            "-d",
            str(duration_days),
        ]
    ).returncode
    if return_code != 0:
        await context.bot.send_message(chat_id, strings["config_generation_error"])
    # else:
    # alternative method for running the sudo command using pexpect:
    # password = "your_password"  # change this to your sudo password
    # child = pexpect.spawn(f"sudo pivpn ovpn add nopass -n {client_name} -d {duration_days}")
    # child.expect("password")
    # child.sendline(password)
    # child.expect(pexpect.EOF)
    # check for any error messages
    # if child.expect(["Error", "Failed", pexpect.EOF]) < 2:
    # an error message was found
    # await context.bot.send_message(chat_id, strings["config_generation_error"])
    else:
        # open the client config file and send it to the user
        file_path = os.path.join(OVPN_FILE_PATH, f"{client_name}.ovpn")
        with open(file_path, "rb") as f:
            await context.bot.send_document(
                chat_id, document=f, filename=f"{client_name}.ovpn"
            )

    # delete the user data to prevent resending the same configuration file
    context.user_data.pop("selected_plan", None)
    context.user_data.pop("duration_days", None)

    # delete the configuration file
    config_file_path = os.path.join(OVPN_FILE_PATH, f"{client_name}.ovpn")

    try:
        # delete the configuration file
        os.remove(config_file_path)
    except Exception as e:
        # handle exceptions, e.g., file not found or permission issues
        logging.error(f"Error deleting files: {str(e)}")


# send a typing indicator in the chat
@send_upload_document_action
# generate client config file for WireGuard
async def wireguard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)
    # get the duration days from the user data
    duration_days = context.user_data.get("duration_days")

    # extract the callback query and chat id from the update object
    query = update.callback_query
    chat_id = query.message.chat_id

    # get the user ID from the Telegram message
    user_id = query.from_user.id
    # generate a unique client name based on the user ID
    client_name = f"user_{user_id}"
    # note: this command requires root privileges
    return_code = subprocess.run(["pivpn", "wg", "add", "-n", client_name]).returncode
    if return_code != 0:
        await context.bot.send_message(chat_id, strings["config_generation_error"])
    # else:
    # alternative method for running the sudo command using pexpect:
    # password = "your_password"  # change this to your sudo password
    # child = pexpect.spawn(f"sudo pivpn wg add -n {client_name}")
    # child.expect("password")
    # child.sendline(password)
    # child.expect(pexpect.EOF)
    # check for any error messages
    # if child.expect(["Error", "Failed", pexpect.EOF]) < 2:
    # an error message was found
    # await context.bot.send_message(chat_id, strings["config_generation_error"])
    else:
        # set expiration timestamp (only for tracking)
        expiry_secs = duration_days * 86400
        expiry_timestamp = int(time.time()) + expiry_secs

        # convert the timestamp to a human-readable date string
        expiry_date = datetime.datetime.utcfromtimestamp(expiry_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        # add client information to a JSON file with the formatted date
        client_info = {"name": client_name, "expires": expiry_date}

        with open(os.path.join(WG_FILE_PATH, f"client_info.json"), "a") as info_file:
            json.dump(client_info, info_file)
            info_file.write("\n")
        # open the client config file and send it to the user
        file_path = os.path.join(WG_FILE_PATH, f"{client_name}.conf")
        with open(file_path, "rb") as f:
            await context.bot.send_document(
                chat_id, document=f, filename=f"{client_name}.conf"
            )
        # send an upload photo indicator in the chat
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO
        )

        config_path = os.path.join(
            WG_FILE_PATH, f"{client_name}.conf"
        )  # Specify the path to the .conf file
        output_file_path = os.path.join(
            QR_CODE_PATH, f"{client_name}.png"
        )  # Specify the output path

        # generate the WireGuard QR code from the config file using qrencode
        subprocess.call(
            [
                "qrencode",
                "-t",
                "png",
                "-o",
                output_file_path,
                "-r",
                config_path,
            ]
        )
        # send the QR code image to Telegram
        qr_code_path = os.path.join(QR_CODE_PATH, f"{client_name}.png")
        with open(qr_code_path, "rb") as f:
            await context.bot.send_photo(chat_id, photo=f)

    # delete the user data to prevent resending the same configuration file
    context.user_data.pop("selected_plan", None)
    context.user_data.pop("duration_days", None)

    # delete the configuration file and QR code image
    config_file_path = os.path.join(WG_FILE_PATH, f"{client_name}.conf")
    qr_code_image_path = os.path.join(QR_CODE_PATH, f"{client_name}.png")

    try:
        # delete the configuration file
        os.remove(config_file_path)
        # delete the QR code image
        os.remove(qr_code_image_path)
    except Exception as e:
        # handle exceptions, e.g., file not found or permission issues
        logging.error(f"Error deleting files: {str(e)}")
