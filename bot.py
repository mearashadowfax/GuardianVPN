# import the required modules
import subprocess  # for running shell commands
import datetime  # for getting the current date/time
import json  # for working with JSON data
import pexpect  # for interacting with command line prompts

# import the Telegram API token from config.py
from config import TELEGRAM_API_TOKEN

telegram_api_token = TELEGRAM_API_TOKEN

# import the Payment provider token from config.py
from config import PAYMENT_PROVIDER_TOKEN

PAYMENT_PROVIDER_TOKEN = PAYMENT_PROVIDER_TOKEN

# import the required Telegram modules
from telegram import Update, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters, ApplicationBuilder, \
    ContextTypes, PreCheckoutQueryHandler


# define a function to get the user's language preference
async def get_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # define a dictionary that maps Telegram's language codes to your supported languages
    supported_languages = {
        'en': 'en',
        'ru': 'ru',
        'fr': 'fr',
        'es': 'es',
        'de': 'de'
    }

    # detect user's language preference and set default to English if not supported
    user_language_code = update.message.from_user.language_code
    language = supported_languages.get(user_language_code, 'en')

    # save the user's language preference in the user_data dictionary
    context.user_data['language'] = language

    return language


async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # create InlineKeyboardMarkup with two buttons
    button1_text = "1 Week - $1"
    button1_callback_data = "product_a"
    button2_text = "1 Month - $3"
    button2_callback_data = "product_b"
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(button1_text, callback_data=button1_callback_data)],
                                   [InlineKeyboardButton(button2_text, callback_data=button2_callback_data)]])

    # send message to the user with the two products to choose from
    chat_id = update.message.chat_id
    description = strings['description']
    await context.bot.send_message(chat_id, description, reply_markup=markup)


# define a function that handles user's callback query when a product is selected
async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # extract the callback query and chat id from the update object
    query = update.callback_query
    chat_id = query.message.chat_id

    # extract the selected product from the callback query data
    product = query.data

    # Check which product is selected and set the corresponding price, title, payload and description
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
    await context.bot.send_invoice(chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, price)


# pre-checkout callback function
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # extract the invoice payload
    invoice_payload = update.pre_checkout_query.invoice_payload
    selected_plan = None

    # check which plan was selected and set the duration accordingly
    if "1 Week" in invoice_payload:
        duration_days = 7
        selected_plan = "1 Week"
    elif "1 Month" in invoice_payload:
        duration_days = 30
        selected_plan = "1 Month"
    else:
        # invalid invoice payload
        await update.pre_checkout_query.answer(ok=False, error_message="Invalid invoice payload")
        return

    # answers the PreQecheckoutQuery
    query = update.pre_checkout_query
    # check the invoice payload, is it from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False PreCheckoutQuery
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

    # store the selected plan and duration in the user data
    user_data = context.user_data
    user_data['selected_plan'] = selected_plan
    user_data['duration_days'] = duration_days


# callback function after contacting the payment provider
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # confirms the successful payment
    successful_payment = strings['successful_payment']
    await update.message.reply_text(successful_payment)
    # call the function generate_config_success() to generate and send the client configuration file
    await generate_config_success(update, context)


# define the command handler for generating OpenVPN client config files
async def generate_config_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user ID from the Telegram message
    user_id = update.message.from_user.id

    # generate a unique client name based on the user ID
    client_name = f"user_{user_id}"

    # define the path for the client config file
    client_config_path = f"/home/sammy/ovpns/{client_name}.ovpn"

    # get the selected plan and duration days from the user data
    user_data = context.user_data
    selected_plan = user_data.get('selected_plan')
    duration_days = user_data.get('duration_days')

    # execute the OpenVPN script to generate the client config file
    # note: this command requires root privileges
    subprocess.run(["pivpn", "add", "nopass", "-n", client_name, "-d", str(duration_days)])

    # alternative method for running the sudo command using pexpect:
    password = "your_password"  # change this to your sudo password
    child = pexpect.spawn(f"sudo pivpn add nopass -n {client_name} -d {duration_days}")
    child.expect("password")
    child.sendline(password)
    child.expect(pexpect.EOF)

    # open the client config file and send it to the user
    with open(client_config_path, "rb") as f:
        await update.message.reply_document(document=f, filename=f"{client_name}.ovpn")

    # send a message to the user confirming the duration of their plan
    if selected_plan is not None:
        duration_message = f"Your GuardianVPN service will be active for {selected_plan}."
        await update.message.reply_text(duration_message)

    # delete the user data to prevent resending the same configuration file
    del user_data['selected_plan']
    del user_data['duration_days']


# define a function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message back to the user when the command /start is issued
    start_message = strings['start_message']
    await update.message.reply_text(start_message)


# define a function to handle the /status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # use subprocess to run the "systemctl status openvpn" command
    output = subprocess.check_output(["systemctl", "status", "openvpn"])

    # extract the relevant line from the output
    active_line = [line for line in output.decode().split('\n') if 'Active:' in line][0]

    # send the extracted line back to the user
    await update.message.reply_text(active_line)


# define a function to handle the /about command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message back to the user in the appropriate language
    about_message = strings['about_message']
    await update.message.reply_text(about_message)


# define a function to handle the /limitations command
async def limitations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message back to the user in the appropriate language
    limitations_message = strings['limitations_message']
    await update.message.reply_text(limitations_message)


# define a function to handle the /privacy command
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message with privacy policy
    privacy_message = strings['privacy_message']
    await update.message.reply_text(privacy_message)


# define a function to handle the /terms command
async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message with terms and conditions
    terms_message = strings['terms_message']
    await update.message.reply_text(terms_message)


# define a function to handle the /help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message with the list of available commands and usage instructions
    help_message = strings['help_message']
    await update.message.reply_text(help_message)


# define a function to handle the /support command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's language preference
    language = await get_language(update, context)

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message with contact information for support
    support_message = strings['support_message']
    await update.message.reply_text(support_message)


# define a function to handle the /tutorial command
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # send a message with instructions on how to use an OpenVPN config file with the OpenVPN app
    tutorial_message = strings['tutorial_message']
    await update.message.reply_text(tutorial_message)


# define a global variable to store the last update date
last_update_date = None


# define a function to handle the /whatsnew command
async def whatsnew(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text("No new updates since the last time you checked.")
    else:
        # send a message with all updates and improvements
        await update.message.reply_text(
            "All updates and improvements:\n"
            "• Added support for French, German, Russian, and Spanish languages based on user's Telegram language "
            "preference\n"
            "• Fixed issue with user authentication and handling the /getapp command\n"
            "• Increased server speed and reliability\n"
            "• Bug fixes and performance improvements\n"
        )

    # update the last update date
    last_update_date = latest_update_date


# define a function to handle the /getapp command
async def getapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load text based on language preference
    with open(f'{language}_strings.json', 'r') as f:
        strings = json.load(f)

    # provide all the download links to the user
    download_links = [
        "Windows: https://openvpn.net/downloads/openvpn-connect-v3-windows.msi",
        "MacOS: https://openvpn.net/downloads/openvpn-connect-v3-macos.dmg",
        "Linux: https://openvpn.net/openvpn-client-for-linux/",
        "Android: https://play.google.com/store/apps/details?id=net.openvpn.openvpn",
        "iOS: https://itunes.apple.com/us/app/openvpn-connect/id590379981?mt=8"
    ]
    # join the download links into a single string
    download_links_str = "\n".join(download_links)

    # send a message back to the user with all the download links
    download_links_message = strings['download_links_message']
    await update.message.reply_text(f"{download_links_message}{download_links_str}")


# handle unknown command
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")


def main():
    # set Telegram bot
    application = ApplicationBuilder().token(telegram_api_token).build()

    # add the command handlers
    application.add_handler(CommandHandler("generate_config", generate_config))
    application.add_handler(CommandHandler("generate_config_success", generate_config_success))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("limitations", limitations))
    application.add_handler(CommandHandler("getapp", getapp))
    application.add_handler(CommandHandler("privacy", privacy))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("terms", terms))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("whatsnew", whatsnew))

    # adds a callback query handler for when the user selects a product to purchase
    application.add_handler(CallbackQueryHandler(select_product))

    # add a message handler to handle unknown commands or messages
    application.add_handler(MessageHandler(filters.ALL, unknown))

    # add a pre-checkout handler to verify and respond to pre-checkout queries
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # add a message handler to handle successful payments and notify the user
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # start the Telegram bot
    application.run_polling()


if __name__ == "__main__":
    main()
