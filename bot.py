# import the required modules
import subprocess   # for running shell commands
import datetime     # for getting the current date/time
import json         # for working with JSON data
import pexpect      # for interacting with command line prompts

# import the Telegram API token from config.py
from config import TELEGRAM_API_TOKEN
telegram_api_token = TELEGRAM_API_TOKEN

# import the required Telegram modules
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes

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

# define the command handler for generating OpenVPN client config files
async def generate_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get the user ID from the Telegram message
    user_id = update.message.from_user.id
    
    # generate a unique client name based on the user ID
    client_name = f"user_{user_id}"
    
    # define the path for the client config file
    client_config_path = f"/home/sammy/ovpns/{client_name}.ovpn"
    
    # execute the OpenVPN script to generate the client config file
    # note: this command requires root privileges
    subprocess.run(["pivpn", "add", "nopass", "-n", client_name, "-d", "30"])
    
    # alternative method for running the sudo command using pexpect:
    # execute the OpenVPN script to generate the client config file
    #password = "your_password"  # change this to your sudo password
    #child = pexpect.spawn(f"sudo pivpn add nopass -n {client_name} -d 30")
    #child.expect("password")
    #child.sendline(password)
    #child.expect(pexpect.EOF)
    
    # open the client config file and send it to the user
    with open(client_config_path, "rb") as f:
        await update.message.reply_document(document=f, filename=f"{client_name}.ovpn")

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
                "• Added support for French, German, Russian, and Spanish languages based on user's Telegram language preference\n"
                )
        else:
            # send a message indicating that there are no new updates
            await update.message.reply_text("No new updates since the last time you checked.")
    else:
        # send a message with all updates and improvements
        await update.message.reply_text(
            "All updates and improvements:\n"
            "• Added support for French, German, Russian, and Spanish languages based on user's Telegram language preference\n"
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

# handle unknow command
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")

def main():
# set Telegram bot
    application = ApplicationBuilder().token(telegram_api_token).build()

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
