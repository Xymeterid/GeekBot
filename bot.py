import codecs
import os
import re
import telebot
from telebot import apihelper

import anilist_api_logic
import service
from flask import Flask, request

TOKEN = "1364491220:AAE_T1pkCAiaaeq-fnNkzx1GyIzcfsCzgFQ"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
server = Flask(__name__)

apihelper.ENABLE_MIDDLEWARE = True

IS_HEROKU = 1

@bot.middleware_handler(update_types=['message'])
def modify_message(bot_instance, message):
    message.no_command_text = re.sub("/(\w*)", "", message.text, 1).strip()


@bot.message_handler(commands=['what_dis_uwu'])
def find_anime(message):
    if message.reply_to_message is None:
        anime_name = message.no_command_text
        if not anime_name:
            html_reply = open("templates/info/what_dis_info.html", encoding="utf-8").read()
            bot.reply_to(message, html_reply)
            return
    else:
        reply_text = message.reply_to_message.text
        name_found = re.search("{.+}", reply_text)
        if name_found is None:
            anime_name = reply_text
        else:
            anime_name = name_found.group()[1:-1]
    json_reply = anilist_api_logic.find_anime_by_name_on_anilist(anime_name.strip())
    reply_message = extract_reply_from_anilist_data(json_reply)
    bot.reply_to(message, reply_message)


@bot.message_handler(regexp="{.+}")
def find_anime_in_brackets(message):
    search_result = re.search("{.+}", message.text)
    anime_name = search_result.group()[1:-1]
    json_reply = anilist_api_logic.find_anime_by_name_on_anilist(anime_name.strip())
    reply_message = extract_reply_from_anilist_data(json_reply)
    bot.reply_to(message, reply_message)


def extract_reply_from_anilist_data(response):
    if response.status_code == 200:

        json_response = (response.json())["data"]["Media"]

        if json_response['isAdult']:
            return open("templates/anime_search_decline_adult_content.html", encoding="utf-8").read()

        if json_response['title']['english'] is None:
            display_name = json_response['title']['romaji']
        else:
            display_name = json_response['title']['english']

        return open("templates/anime_name_search_results.html", encoding="utf-8").read().format(
                         display_name,
                         json_response['siteUrl'],
                         "https://myanimelist.net/anime/{}".format(json_response["idMal"])
                     )
    else:
        return open("templates/anime_search_nothing_found.html", encoding="utf-8").read()


@bot.message_handler(commands=['add_alias'])
def add_alias(message):
    splits = message.no_command_text.split(" == ")
    if len(splits) < 2:
        bot.reply_to(message, open("templates/info/add_alias_info.html", encoding="utf-8").read())
        return

    key = (splits[0]).strip().lower()
    value = (splits[1]).strip().lower()

    result = service.aliases_service.insert_alias(key, value, message.from_user.username)

    if result == 1:
        bot.reply_to(message, open("templates/alias_addition_success.html", encoding="utf-8").read())
    if result == 2:
        bot.reply_to(message, open("templates/alias_modification_success.html", encoding="utf-8").read())


@bot.message_handler(commands=['show_aliases'])
def show_all_aliases(message):
    data = list(service.aliases_service.get_all_aliases())
    if len(data) == 0:
        bot.reply_to(message, open("templates/aliases_list_empty.html", encoding="utf-8").read())
        return
    res = ""
    for alias in data:
        res += "• " + alias['alias_key'] + " == " + alias['alias_value'] + "\n"
    bot.reply_to(message, res)


@bot.message_handler(commands=['delete_alias'])
def delete_alias(message):
    if message.no_command_text == '':
        bot.reply_to(message, open("templates/info/delete_alias_info.html", encoding="utf-8").read())
        return

    res = service.aliases_service.delete_alias(message.no_command_text)
    if res.deleted_count >= 1:
        bot.reply_to(message, open("templates/alias_deletion_success.html", encoding="utf-8").read())
    else:
        bot.reply_to(message, open("templates/alias_deletion_failure_no_such_alias.html", encoding="utf-8").read())


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
    if IS_HEROKU == 1:
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    else:
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0)

