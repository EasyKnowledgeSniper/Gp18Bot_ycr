from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    ContextTypes, filters
import configparser
import os
import logging

import redis
global redis1

import json


def main():
    global redis1

    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    
    redis1 = redis.Redis(host=(os.environ['HOST']), password=
    (os.environ['PASSWORD']), port=(os.environ['REDISPORT']))
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("write", write))
    dispatcher.add_handler(CommandHandler("checkAll", checkAll))
    # dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("photo",photo))
    dispatcher.add_handler(CommandHandler("cancel", cancel))


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Good day, ' + str(context.args[0]) + '!')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        # global redis1
        logging.info('Keyword: ' + context.args[0])
        # logging.info(context.args[1])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        # in Redis database, automatically set 'msg' as a key, increase its value by 1
        redis1.incr(msg) 
        update.message.reply_text('You have said ' + msg + ' for ' +
        redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        # Reply to the user with a message suggesting the correct command format.
        update.message.reply_text('Usage: /add <keyword>')


# start a conversation by entering '/start'
def start(update: Update, context) -> int:
    reply_keyboard = [["/write", "/checkAll", "/photo", "/cancel"]]

    update.message.reply_text(
        "Hi! My name is Gp18 Bot. I will hold a conversation with you.\n\n"
        
        "Do you want to write a movie review, read a movie review, see the hiking information?\n"
        "1. send /write to write a movie review\n"
        "2. send /checkAll to read all movie reviews\n"
        "3. send /photo to see a hiking route and a photo\n"
        "4. Send /cancel to stop talking to me\n",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="write, checkAll, photo or cancel"
        ),
    )
    return write


# write a review in the format of '/write <movie_title>. <movie_review>'
def write(update: Update, context: CallbackContext) -> None:
    
    try:
        input_text = ' '.join(context.args) # transfer a list to string
        # detect the first full stop, split the string as a separator.
        movie_title, movie_review = input_text.split('.', maxsplit=1)

        logging.info('context: ' + movie_title)
        logging.info('review: ' + movie_review)
        # store to Redis database with 'movie_title' as the key.
        redis1.set(movie_title, movie_review)
        # redis1.__setitem__(title, review)
        update.message.reply_text('Movie Title: ' + movie_title + '\nMovie Review: ' +
        redis1.get(movie_title).decode('UTF-8'))

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /write <movie_title>. <movie_review>')


def checkAll(update: Update, context) -> None:
    try:
        movie_titles_list = redis1.keys('*') # group all movie titles into a list
        msg = ''
        for movie_title in movie_titles_list:
            m_title_str = movie_title.decode('UTF-8') # change bytes format to string format
            # get the corresponding movie review
            m_review_str = redis1.get(movie_title).decode('UTF-8')

            # concatenate the movie title and review
            msg += f'Movie Title: {m_title_str}\nMovie Review: {m_review_str}\n\n'

        update.message.reply_text(msg)
        
    except (IndexError, ValueError):
        update.message.reply_text('error')



# see a hiking route and a photo,
def photo(update: Update, context: CallbackContext) -> None:

    # read mountains' information from 'mountains.json'
    with open("mountains.json", 'r') as f:
        mountains = json.load(f)

    for mountain_name, mountain_info in mountains.items():
        # 将每条hiking route以多个键值对的形式存储在redis中，key为山峰的名称，value为包含img_url和description两个字段的hash map
        redis1.hmset(mountain_name, {'img_url': mountain_info['img_url'], 'description': mountain_info['description']})

    try:
        # get the mountain name from the input
        mountain_name = ' '.join(context.args)
        logging.info(mountain_name)

        # get description from Redis according to mountain name
        # mountain_info = redis1.hgetall(mountain_name)

        # get the URL and description according to mountain_name
        img_url = redis1.hget(mountain_name, 'img_url')
        description = redis1.hget(mountain_name, 'description')
        

        logging.info(mountain_info)
        logging.info(img_url)
        logging.info(description)
        

        # if not mountain_info:
        #     context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, no information found for the specified mountain.")
        #     return
        
        # # check if img_url and description exist in mountain_info dictionary
        # if 'img_url' not in mountain_info or 'description' not in mountain_info:
        #     context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, the information for the specified mountain is incomplete.")
        #     return

        
        update.message.reply_text('Mountain Name: ' + mountain_name + '\n\n' + 'Mountain Image: ' + img_url.decode('UTF-8')+ '\n\n' + 'Hiking Route: ' + description.decode('UTF-8'))


    except (IndexError, ValueError):
        update.message.reply_text('Usage: /photo <mountain_name>')


# def check(update: Update, context: CallbackContext) -> None:
#     try:
#         # global redis1
#         title = context.args[0]
#         review = redis1.get(title).decode('UTF-8')
#         # logging.info(title.decode('UTF-8'))
#         update.message.reply_text('Title: ' + title + '\nReview: \n' + review)
#     except (IndexError, ValueError):
#         update.message.reply_text('error')


def cancel(update: Update, context) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

if __name__ == '__main__':
    
    main()