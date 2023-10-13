# import the Telegram API token from config.py
from config import TELEGRAM_API_TOKEN

# import the required Telegram modules
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    PreCheckoutQueryHandler,
)

# import the required modules
from modules.pre_payment_functions import *
from modules.payment_functions import *
from modules.config_functions import *
from modules.info_functions import *
from modules.download_links_functions import *
from modules.utils import *
from modules.language_functions import *

# enable logging
logging.basicConfig(level=logging.INFO)


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
