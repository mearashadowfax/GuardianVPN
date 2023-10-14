# import the required modules
import json  # for working with JSON data
from modules.config_actions import *
from modules.language_functions import *

# import the required Telegram modules
from telegram.ext import ContextTypes


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
    language, language_file_path = await get_language(update, context)

    # load text based on language preference
    with open(language_file_path, "r") as f:
        strings = json.load(f)

    # confirms the successful payment
    successful_payment = strings["successful_payment"]
    await update.message.reply_text(successful_payment)
    # call the function generate_config_success() to generate and send the client configuration file
    await generate_config_success(update, context)
