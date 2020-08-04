import telebot
import os
from flask import Flask, request
import requests

TOKEN = "1364491220:AAE_T1pkCAiaaeq-fnNkzx1GyIzcfsCzgFQ"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

nameSearchQuery = '''
query ($id: Int) {
  Media (search: "tanya", type: ANIME) {
    title {
      romaji
      english
    }
    siteUrl
    description
  }
}
'''


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Welcome!')


@bot.message_handler(commands=['whatDisUwu'])
def find_anime(message):
    bot.reply_to(message, message.text)


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://geek-club-bot.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
