# import the required Telegram modules
from telegram import Update
from telegram.ext import ContextTypes


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
