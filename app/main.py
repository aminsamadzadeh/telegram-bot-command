#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to run command in server

import subprocess

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

import os
from configparser import SafeConfigParser

config = SafeConfigParser()
config.read(os.path.join(os.path.dirname(__file__),'config.ini'))

def get_option(section, option):
	try:
		return config.get(section, option)
	except:
		return

def check_user_permission(username):
    users = get_option('permission','users').split(",")
    
    for user in users:
        if user == username:
            return True

    return False

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING,COMMAND = range(2)


def start(bot, update):
    user = update.message.from_user
    if check_user_permission(user.username):
        reply_keyboard = [['Command']]
        update.message.reply_text(
            "select one option:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSING    
    else:
        update.message.reply_text("permission denied!")
        return ConversationHandler.END
    
    return ConversationHandler.END


def choosing(bot, update):
    if update.message.text == "Command":
        update.message.reply_text("enter your command:")
        return COMMAND
    else:
        return ConversationHandler.END

def command(bot, update):
    cmd = update.message.text.split(" ")
    logger.info(cmd)
    res = subprocess.check_output(cmd, shell=True)
    res = res.decode('utf8')
    logger.info(res)
    update.message.reply_text(res)
    return ConversationHandler.END

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    token = get_option('bot','token')
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.text, choosing)],
            COMMAND: [MessageHandler(Filters.text, command)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
