# import the required modules
import asyncio  # for asynchronous programming
import subprocess  # for running shell commands
import datetime  # for getting the current date/time
import json  # for working with JSON data
import time  # for working with time-related operations
import pexpect  # for interacting with command line prompts
import logging  # for logging to help debug and troubleshoot the program
from functools import wraps  # for using function decorators

# import the Telegram API token from config.py
from config import TELEGRAM_API_TOKEN

TELEGRAM_API_TOKEN = TELEGRAM_API_TOKEN

# import the Payment provider token from config.py
from config import PAYMENT_PROVIDER_TOKEN

PAYMENT_PROVIDER_TOKEN = PAYMENT_PROVIDER_TOKEN

# import the required Telegram modules
from telegram.constants import ChatAction
from telegram import Update, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes,
    PreCheckoutQueryHandler,
    ConversationHandler,
)

# enable logging
logging.basicConfig(level=logging.INFO)


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


# define a function to get the user's language preference
async def get_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # define a dictionary that maps Telegram's language codes to your supported languages
    supported_languages = {"en": "en", "ru": "ru", "fr": "fr", "es": "es", "de": "de"}

    # detect user's language preference and set default to English if not supported
    user_language_code = update.message.from_user.language_code
    language = supported_languages.get(user_language_code, "en")

    # save the user's language preference in the user_data dictionary
    context.user_data["language"] = language

    return language


# define a function to display a message with streaming text
@send_typing_action
async def display_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, delimiter: str
):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
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
        await asyncio.sleep(0.5)


async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
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


# define a function that handles user's callback query when a product is selected
async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # extract the callback query and chat id from the update object
    query = update.callback_query
    chat_id = query.message.chat_id

    # extract the selected product from the callback query data
    product = query.data

    # check which product is selected and set the corresponding price, title, payload and description
    if product == "product_a":
        price = [LabeledPrice("1 Week", 1 * 100)]
        title = "VPN Access Pass - 1 Week"
        description = "Get one week of unlimited access to GuardianVPN"
        payload = "1 Week"
    elif product == "product_b":
        price = [LabeledPrice("1 Month", 3 * 100)]
        title = "VPN Access Pass - 1 Month"
        description = "Get one month of unlimited access to GuardianVPN"
        payload = "1 Month"
    else:
        # handle invalid product selection by returning
        return

    # set the payment currency
    currency = "USD"

    # send the invoice to the user with the selected product price
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, price
    )


# pre-checkout callback function
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # extract the invoice payload
    invoice_payload = update.pre_checkout_query.invoice_payload
    selected_plan = None
    duration_days = None

    # check which plan was selected and set the duration accordingly
    if "1 Week" in invoice_payload:
        duration_days = 7
        selected_plan = "1 Week"
    elif "1 Month" in invoice_payload:
        duration_days = 30
        selected_plan = "1 Month"

    # answers the PreCheckoutQuery
    query = update.pre_checkout_query
    # check the invoice payload, is it from your bot?
    if query.invoice_payload == "1 Week" or query.invoice_payload == "1 Month":
        await query.answer(ok=True)
    # answer False PreCheckoutQuery
    else:
        await query.answer(ok=False, error_message="Something went wrong...")

    # store the selected plan and duration in the user data
    user_data = context.user_data
    user_data["selected_plan"] = selected_plan
    user_data["duration_days"] = duration_days


# callback function after contacting the payment provider
async def successful_payment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
        strings = json.load(f)

    # confirms the successful payment
    successful_payment = strings["successful_payment"]
    await update.message.reply_text(successful_payment)
    # call the function generate_config_success() to generate and send the client configuration file
    await generate_config_success(update, context)


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


# callback function after choosing the VPN protocol
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = context.user_data.get("language", "en")

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
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
    language = context.user_data.get("language", "en")

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
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
        file_path = f"/home/sammy/ovpns/{client_name}.ovpn"
        with open(file_path, "rb") as f:
            await context.bot.send_document(
                chat_id, document=f, filename=f"{client_name}.ovpn"
            )

    # delete the user data to prevent resending the same configuration file
    context.user_data.pop("selected_plan", None)
    context.user_data.pop("duration_days", None)


# send a typing indicator in the chat
@send_upload_document_action
# generate client config file for WireGuard
async def wireguard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = context.user_data.get("language", "en")

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
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
        # set expiration timestamp (only for Wireguard config)
        expiry_secs = duration_days * 86400
        expiry_timestamp = int(time.time()) + expiry_secs
        expiry_date = datetime.datetime.utcfromtimestamp(expiry_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
        config_file = f"/home/sammy/configs/{client_name}.conf"
        post_up = f'Expires = "{expiry_date}"\n'
        # add PostUp command to client configuration file
        with open(config_file, "a") as f:
            f.write(post_up)
        # open the client config file and send it to the user
        with open(f"/home/sammy/configs/{client_name}.conf", "rb") as f:
            await context.bot.send_document(
                chat_id, document=f, filename=f"{client_name}.conf"
            )
        # send an upload photo indicator in the chat
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO
        )

        # generate the WireGuard QR code from the config file using qrencode
        subprocess.call(
            [
                "qrencode",
                "-t",
                "png",
                "-o",
                f"/home/sammy/configs/{client_name}.png",
                "-r",
                f"/home/sammy/configs/{client_name}.conf",
            ]
        )
        # use pexpect to generate the QR code and capture the output
        # set the path to the qrencode command
        # qrencode_path = "/usr/bin/qrencode"
        # specify the path to the directory containing the config files
        # config_path = "/home/sammy/configs/"
        # set the parameters for the qrencode command
        # qrencode_args = ["-t", "png", "-o", f"{config_path}{client_name}.png", "-r", f"{config_path}{
        # client_name}.conf"]
        # spawn a child process to execute the qrencode command
        # child = pexpect.spawn(qrencode_path, qrencode_args)
        # wait for the command to complete
        # child.expect(pexpect.EOF)
        # send the QR code image to Telegram
        # with open(f"{config_path}{client_name}.png", "rb") as f:
        # await context.bot.send_photo(chat_id, photo=f)
        # send the QR code image to Telegram
        with open(f"/home/sammy/configs/{client_name}.png", "rb") as f:
            await context.bot.send_photo(chat_id, photo=f)

    # delete the user data to prevent resending the same configuration file
    context.user_data.pop("selected_plan", None)
    context.user_data.pop("duration_days", None)


# call the display_message function for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "start_message", ".")


# send a typing indicator in the chat
@send_typing_action
# define a function to handle the /status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # use subprocess to run the "systemctl status openvpn" command
    output = subprocess.check_output(["systemctl", "status", "openvpn"])

    # extract the relevant line from the output
    active_line = [line for line in output.decode().split("\n") if "Active:" in line][0]

    # send the extracted line back to the user
    await update.message.reply_text(active_line)


# call the display_message function for the /about command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "about_message", ".")


# call the display_message function for the /limitations command
async def limitations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "limitations_message", "• ")


# call the display_message function for the /privacy command
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "privacy_message", "• ")


# call the display_message function for the /help command
async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "help_message", "/")


# call the display_message function for the /terms command
async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "terms_message", "•")


# call the display_message function for the /support command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "support_message", ".")


# call the display_message function for the /tutorial command
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await display_message(update, context, "tutorial_message", ". ")


# define a global variable to store the last update date
last_update_date = None


# send a typing indicator in the chat
@send_typing_action
# define a function to handle the /whatsnew command
async def whatsnew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = await get_language(update, context)

    # load text based on language preference
    with open(f"{language}_strings.json", "r") as f:
        strings = json.load(f)

    global last_update_date

    # set the current date as the latest update date
    latest_update_date = datetime.date.today()

    # check if there is a last update date recorded
    if last_update_date:
        # check if there are any updates made after the last update date
        if latest_update_date > last_update_date:
            # send a message with latest updates and improvements
            await update.message.reply_text(
                f"New updates and improvements since {last_update_date}:\n"
                "• Added support for French, German, Russian, and Spanish languages based on user's Telegram language "
                "preference\n"
            )
        else:
            # send a message indicating that there are no new updates
            await update.message.reply_text(
                "No new updates since the last time you checked."
            )
    else:
        # send a message with all updates and improvements
        all_updates = strings["all_updates"]
        await update.message.reply_text(all_updates)

    # update the last update date
    last_update_date = latest_update_date


# stages
START, END = range(2)
# callback data
APP_OPTIONS = ["OpenVPN", "WireGuard"]
APP_LETTERS = ["O", "W"]
OS_OPTIONS = ["Windows", "macOS", "Linux", "Android", "iOS"]
OS_LETTERS = ["Wi", "M", "L", "A", "I"]


# function to get app selection from user
async def getapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # set up the keyboard with app options and their assigned letters (callback data)
    keyboard = [
        [
            InlineKeyboardButton(option, callback_data=letter)
            for option, letter in zip(APP_OPTIONS, APP_LETTERS)
        ]
    ]

    get_app = InlineKeyboardMarkup(keyboard)
    # ask user to select an app
    await update.message.reply_text(
        "Please select the VPN app you want to download:", reply_markup=get_app
    )

    return START


# function to handle OS selection from user
async def handle_os_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get CallbackQuery from Update
    query = update.callback_query
    await query.answer()

    selected_app = query.data
    context.user_data["selected_app"] = selected_app
    # set up the keyboard with OS options and their assigned letters (callback data)
    keyboard = [
        [
            InlineKeyboardButton(option, callback_data=letter)
            for option, letter in zip(OS_OPTIONS, OS_LETTERS)
        ]
    ]

    os_selection = InlineKeyboardMarkup(keyboard)
    # ask user to select an OS
    await query.edit_message_text(
        text="Choose your operating system:", reply_markup=os_selection
    )

    return END


# function to get download link based on user's selections
async def get_download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_os = query.data
    context.user_data["selected_os"] = selected_os

    selected_app = context.user_data.get("selected_app")
    selected_os = context.user_data.get("selected_os")

    # load the download_links.json file and get the download link based on the user's app and OS selections
    with open("download_links.json") as f:
        data = json.load(f)
    url = data[selected_app][selected_os]
    # display the download link to the user
    await query.edit_message_text(text=f"Here's your download link: {url}")

    return ConversationHandler.END


# send a typing indicator in the chat
@send_typing_action
# handle unknown command
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")


def main():
    # set Telegram bot
    application = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    # add the command handlers
    application.add_handler(CommandHandler("generate_config", generate_config))
    application.add_handler(
        CommandHandler("generate_config_success", generate_config_success)
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_message))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("limitations", limitations))
    application.add_handler(CommandHandler("privacy", privacy))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("terms", terms))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("whatsnew", whatsnew))

    # add a pre-checkout handler to verify and respond to pre-checkout queries
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # add a message handler to handle successful payments and notify the user
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    # define the ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("getapp", getapp)],
        states={
            START: [
                CallbackQueryHandler(handle_os_selection, pattern=f"^{letter}$")
                for letter in APP_LETTERS
            ],
            END: [
                CallbackQueryHandler(get_download_link, pattern=f"^{letter}$")
                for letter in OS_LETTERS
            ],
        },
        fallbacks=[],
        allow_reentry=True,
    )

    # add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # add a callback query handler for when the user selects a product to purchase
    application.add_handler(
        CallbackQueryHandler(select_product, pattern="^(product_a|product_b)$")
    )

    # add a callback query handler for when the user selects a VPN protocol
    application.add_handler(
        CallbackQueryHandler(button_callback, pattern="^(openvpn|wireguard|suggest)$")
    )

    # add a message handler to handle unknown commands or messages
    application.add_handler(MessageHandler(filters.ALL, unknown))

    # start the Telegram bot
    application.run_polling()


if __name__ == "__main__":
    main()
