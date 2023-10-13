# import the required modules
import os

# import the required Telegram modules
from telegram import Update
from telegram.ext import ContextTypes

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the languages directory relative to the script's location
languages_dir = os.path.join(script_dir, "..", "languages")


# Define a function to get the user's language preference and the language file path
async def get_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    # Define a dictionary that maps Telegram's language codes to your supported languages
    supported_languages = {"en": "en", "ru": "ru", "fr": "fr", "es": "es", "de": "de"}

    # Detect the user's language preference and set the default to English if not supported
    user_language_code = update.message.from_user.language_code
    language = supported_languages.get(user_language_code, "en")

    # Save the user's language preference in the user_data dictionary
    context.user_data["language"] = language

    # Construct the language file path based on the user's language preference
    language_file_path = os.path.join(languages_dir, f"{language}_strings.json")

    return language, language_file_path
