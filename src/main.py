import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    """Answer to /start"""
    # todo: explain commands
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext):
    """Answer to /help"""
    # todo: explain commands
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext):
    """Answer to message from user"""
    user_message_text = update.message.text
    words = user_message_text.split(" ")

    # todo: weather chat (/weather -> start -> end -> antwort/bild)
    if words[0] == "weather" and len(words) == 3:
        start_location = words[1]
        end_location = words[2]

        update.message.reply_text(f"Calculating Weather along Route from {start_location} to {end_location}.")
        # todo: return weather information
        update.message.reply_text("Weatherinformation")
    else:
        update.message.reply_text("Didnt understand. Syntax is \"/weather <start_location> <end_location>\". Please try again.")


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("../config/settings.cfg")
    telegram_token = config["telegram"]["token"]

    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

# todo: folium map https://github.com/GIScience/openrouteservice-py/blob/master/examples/basic_example.ipynb