# import the required modules
import os
import subprocess
import platform
import json

# import the Telegram API token from config.py
from config import TELEGRAM_API_TOKEN
telegram_api_token = TELEGRAM_API_TOKEN

# import the required Telegram modules
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes

# define the command handler for generating OpenVPN client config files
async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user ID from the Telegram message
    user_id = update.message.from_user.id
    
    # generate a unique client name based on the user ID
    client_name = f"user_{user_id}"
    
    # define the path for the client config file
    client_config_path = f"/home/sammy/ovpns/{client_name}.ovpn"
    
    # execute the OpenVPN script to generate the client config file
    subprocess.run(["sudo", "pivpn", "add", "nopass", "-n", client_name, "-d", "30"])
    
    # open the client config file and send it to the user
    with open(client_config_path, "rb") as f:
        update.message.reply_document(document=f, filename=f"{client_name}.ovpn")

# define a function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # detect user's language preference
    user_language_code = update.message.from_user.language_code
    
    # set default language to English
    language = 'en'
    
    # map Telegram's language codes to your supported languages
    if user_language_code == 'ru':
        language = 'ru'
    elif user_language_code == 'fr':
        language = 'fr'
    elif user_language_code == 'es':
        language = 'es'
    elif user_language_code == 'de':
        language = 'de'
    
    # save the user's language preference in the user_data dictionary
    context.user_data['language'] = language

     # load translated text based on language preference
    if language == 'en':
        # send a message back to the user when the command /start is issued
        start_message = ("Hello! Welcome to GuardianVPN.\n"
    "To use the VPN, simply generate a new configuration file by typing /generate_config.\n"
    "The configuration file will be sent to you as a document.\n"
    "If you need help, type /help.\n"
    "Thank you for choosing GuardianVPN!\n"
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        start_message = strings['start_message']
    
    # send a message back to the user in the appropriate language
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
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message back to the user with the desired text
        about_message = ("GuardianVPN is a secure VPN bot that encrypts your data with the industry-standard OpenVPN protocol, ensuring full confidentiality, authentication, and integrity.\n"
        "Connect to servers worldwide, mask your IP address, and bypass website censorship and geographical blocks.\n"
        "Our no-logs and no-customer-data policy guarantees your data always remains private. Thank you for choosing GuardianVPN to protect your online privacy and security."
        )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        about_message = strings['about_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(about_message)
    
# define a function to handle the /limitations command
async def limitations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message back to the user with the desired text
        limitations_message = ("While we offer a robust and reliable VPN service, there are some limitations to what it can't do:\n"
    "• Defend against cyber threats and protect against identity theft\n"
    "• Secure your passwords and hide your phone location\n"
    "• Achieve complete privacy and anonymity online\n"
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        limitations_message = strings['limitations_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(limitations_message)

# define a function to handle the /privacy command
async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message back to the user with the desired text
        privacy_message = ("Our VPN service is fully committed to protecting user data and maintaining user confidentiality:\n"
    "• No traffic, timestamp, DNS, bandwidth, or IP logging\n"
    "• Activity is only tracked by the total number of active connections at any given time\n"
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        privacy_message = strings['privacy_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(privacy_message)

 # define a function to handle the /terms command
async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message back to the user with the desired text   
        terms_message = ("Terms of Service for GuardianVPN:\n"
    "By using GuardianVPN, you agree to the following terms and conditions:\n"
    "• You will not use our service to engage in any illegal or criminal activities, including but not limited to hacking, port scanning, transmitting viruses, distributing pirated materials, engaging in child pornography, or promoting terrorism.\n" 
    "• You will not use our service to send unsolicited data, including spam emails or unsolicited instant messages.\n"
    "• You will not use our service to threaten or harass others.\n"
    "• You will not share your account with others, and you are responsible for all activities that occur under your account.\n"
    "• You agree not to pay for the service with a stolen credit card, and you will not resell or attempt to resell GuardianVPN accounts or services without our express written permission.\n" 
    "• We provide our service 'as is' and do not guarantee its speed or uninterrupted availability. We are not liable for any damages or loss of profit resulting from the use of our services.\n" 
    "• We reserve the right to modify our Terms of Service, and your continued use of our service after any modifications will constitute your acceptance of the new Terms.\n" 
    "• If you violate any of these terms, we reserve the right to terminate your service without notice and without refund.\n"
    "By agreeing to these terms, you acknowledge that the main goal of GuardianVPN is to protect your privacy and that we do not condone or promote illegal activities of any sort. If you have any questions about our policy, please contact us.\n"
    "Refunds:\n"
    "You may request a complete refund within 30 days of your payment if you are not satisfied for any reason. To initiate the refund process, please share your Telegram Chat ID through our support chat."
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        terms_message = strings['terms_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(terms_message)

# define a function to handle the /help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message with the list of available commands and usage instructions
        help_message = ("Welcome to the GuardianVPN Bot help page! Here are some commands you can use:\n"
        "/about - Get information about the bot and its features\n"
        "/generate_config - Receive an ovpn. configuration file\n"
        "/getapp - Download the OpenVPN app based on your OS\n"
        "/limitations - Learn about the bot's limitations\n"
        "/privacy - View our privacy policy\n"
        "/status - Check the status of your VPN connection\n"
        "/terms - Read our terms and conditions\n"
        "/tutorial - Learn how to use an OpenVPN config file with the OpenVPN app\n"
        "/whatsnew - View latest updates and improvements to the bot and the VPN service\n"
        "If you need help or encounter any issues, please contact us using the /support command. Thank you for using our GuardianVPN bot!"
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        help_message = strings['help_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(help_message)

# define a function to handle the /support command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message with contact information for support
        support_message = (
        "If you need help or encounter any issues with the GuardianVPN Bot, please contact us at https://t.me/GuardianVPN_Support \n"
        "We'll be happy to assist you with any questions or concerns you may have!"
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        support_message = strings['support_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(support_message)

# define a function to handle the /tutorial command
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get user's language preference from user_data dictionary
    language = context.user_data.get('language', 'en')

    # load translated text based on language preference
    if language == 'en':
        # send a message with instructions on how to use an OpenVPN config file with the OpenVPN app
        tutorial_message = (
        "To use the OpenVPN app with the GuardianVPN Bot, you will need to download and import an OpenVPN configuration file (.ovpn). Here's how to do it:\n"
        "1. Download the .ovpn file generated by the GuardianVPN Bot to your device.\n"
        "2. Install the OpenVPN app on your device using /getapp command.\n"
        "3. Open the OpenVPN app and tap the 'Import' button.\n"
        "4. Navigate to the directory where you downloaded the .ovpn file and select it.\n"
        "5. Tap the 'Connect' button to connect to the GuardianVPN server.\n"
        "That's it! You should now be connected to the GuardianVPN server. If you encounter any issues, please contact us using the /support command."
    )
    else:
        with open(f'{language}_strings.json', 'r') as f:
            strings = json.load(f)
        tutorial_message = strings['tutorial_message']

    # send a message back to the user in the appropriate language
    await update.message.reply_text(tutorial_message)

# define a function to handle the /whatsnew command
async def whatsnew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # send a message with latest updates and improvements
    await update.message.reply_text(
        "17.03.2023: Bug fixes and performance improvements\n"
        )

# define a function to handle the /download command
async def getapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user's operating system
    os_type = platform.system()
    # choose the appropriate download link based on the user's operating system
    if os_type == "Windows":
        download_link = "https://openvpn.net/downloads/openvpn-connect-v3-windows.msi"
    elif os_type == "Darwin":
        download_link = "https://openvpn.net/downloads/openvpn-connect-v3-macos.dmg"
    elif os_type == "Linux":
        download_link = "https://openvpn.net/openvpn-client-for-linux/"
    elif os_type == "Android":
        download_link = "https://play.google.com/store/apps/details?id=net.openvpn.openvpn"
    elif os_type == "iOS":
        download_link = "https://itunes.apple.com/us/app/openvpn-connect/id590379981?mt=8"    
    else:
        # if the user's operating system is not recognized, send an error message
        await update.message.reply_text("Sorry, we don't have a download link for your operating system.")
        return
    # send a message back to the user with the download link
    await update.message.reply_text(f"Here's the download link for your operating system:\n{download_link}")

# handle unknow command
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I don't understand your command.")

# set Telegram bot
    application = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

# add the command handlers
    application.add_handler(CommandHandler("generate_config", generate_config))
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

# unknown command handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

# start the Telegram bot
    application.run_polling()

if __name__ == "__main__":
    main()