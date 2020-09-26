import os
import re
import telebot
from telebot import apihelper

import anilist_api_logic
from flask import Flask, request

from dao import user_dao, aliases_dao

TOKEN = "1364491220:AAE_T1pkCAiaaeq-fnNkzx1GyIzcfsCzgFQ"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
server = Flask(__name__)

apihelper.ENABLE_MIDDLEWARE = True

IS_HEROKU = 0


@bot.middleware_handler(update_types=['message'])
def modify_message(bot_instance, message):
    if message.text is None:
        return
    message.no_command_text = re.sub("/(\w*)", "", message.text, 1).strip()
    message.no_command_text = re.sub("@(\w*)", "", message.no_command_text, 1).strip()
    if user_dao.find_by_tg_id(message.from_user.id) is not None:
        message.user_registered = True
    else:
        message.user_registered = False


"-----------------------------------------------------------------------"
"----------------------------SEARCH COMMANDS----------------------------"
"-----------------------------------------------------------------------"


@bot.message_handler(commands=['what_dis_uwu'])
def find_anime_by_command(message):
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
    bot.reply_to(message, find_anime(anime_name))


@bot.message_handler(regexp="{.+}")
def find_anime_in_brackets(message):
    search_result = re.search("{.+}", message.text)
    anime_name = search_result.group()[1:-1]
    bot.reply_to(message, find_anime(anime_name))


def find_anime(name):
    response = anilist_api_logic.find_anime_by_name_on_anilist(name.strip())
    if response.status_code != 200:
        return open("templates/anime_search_nothing_found.html", encoding="utf-8").read()

    json_response = (response.json())["data"]["Media"]

    if json_response['isAdult']:
        return open("templates/anime_search_decline_adult_content.html", encoding="utf-8").read()

    if json_response['title']['english'] is None:
        display_name = json_response['title']['romaji']
    else:
        display_name = json_response['title']['english']
    result_prefix = open("templates/anime_name_search_results.html", encoding="utf-8").read().format(
        display_name,
        json_response['siteUrl'],
        "https://myanimelist.net/anime/{}".format(json_response["idMal"])
    )

    anilist_id = json_response['id']
    result_postfix = ""
    all_users = user_dao.get_all_with_a_list()

    for user in all_users:
        if user['a_list']['type'] == "anilist":
            response_for_user = anilist_api_logic.find_anime_in_users_anilist(anilist_id, user['a_list']['username'])
            if response_for_user.status_code == 200:
                response_for_user_json = (response_for_user.json())['data']['MediaList']
                user_info = bot.get_chat_member(user["tg_id"], user["tg_id"]).user
                result_postfix += get_user_display_name(user_info) \
                    + " - " + str(response_for_user_json['score']) + "/10\n"

    if result_postfix != "":
        result_prefix += "\n<b>В анімелістах у:</b>\n" + result_postfix

    return result_prefix


"----------------------------------------------------------------------"
"----------------------------ALIAS COMMANDS----------------------------"
"----------------------------------------------------------------------"


@bot.message_handler(commands=['add_alias'])
def add_alias(message):
    splits = message.no_command_text.split(" == ")
    if len(splits) < 2:
        bot.reply_to(message, open("templates/info/add_alias_info.html", encoding="utf-8").read())
        return

    key = (splits[0]).strip().lower()
    value = (splits[1]).strip().lower()

    result = aliases_dao.insert(key, value, message.from_user.username)

    if result == 1:
        bot.reply_to(message, open("templates/alias_addition_success.html", encoding="utf-8").read())
    if result == 2:
        bot.reply_to(message, open("templates/alias_modification_success.html", encoding="utf-8").read())


@bot.message_handler(commands=['show_aliases'])
def show_all_aliases(message):
    data = list(aliases_dao.get_all())
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

    res = aliases_dao.delete(message.no_command_text)
    if res.deleted_count >= 1:
        bot.reply_to(message, open("templates/alias_deletion_success.html", encoding="utf-8").read())
    else:
        bot.reply_to(message, open("templates/alias_deletion_failure_no_such_alias.html", encoding="utf-8").read())


"---------------------------------------------------------------------"
"----------------------------USER COMMANDS----------------------------"
"---------------------------------------------------------------------"


@bot.message_handler(commands=['register_me'])
def register_user(message):
    user_id = message.from_user.id
    if user_dao.find_by_tg_id(user_id) is not None:
        bot.reply_to(message, open("templates/user_already_registered.html", encoding="utf-8").read())
    else:
        user_dao.insert(user_id)
        bot.reply_to(message, open("templates/user_created.html", encoding="utf-8").read())


"--------------------------------------------------------------------------"
"----------------------------ANIMELIST COMMANDS----------------------------"
"--------------------------------------------------------------------------"


@bot.message_handler(commands=['add_list'])
def add_a_list(message):
    if not message.user_registered:
        bot.reply_to(message, open("templates/user_not_registered.html", encoding="utf-8").read())
        return
    if re.search("https://((anilist\.co/user/.+/animelist)|(myanimelist\.net/profile/.+))",
                 message.no_command_text) is None:
        bot.reply_to(message, open("templates/a_list_site_not_supported.html", encoding="utf-8").read())
        return
    user_dao.modify_a_list(message.from_user.id, message.no_command_text)
    bot.reply_to(message, open("templates/a_list_updated.html", encoding="utf-8").read())


@bot.message_handler(commands=['my_list'])
def my_a_list(message):
    get_a_list(message, message.from_user)


@bot.message_handler(commands=['his_list'])
def his_a_list(message):
    if message.reply_to_message is None:
        bot.reply_to(message, open("templates/info/his_list_info.html", encoding="utf-8").read())
        return
    get_a_list(message, message.reply_to_message.from_user)


def get_a_list(message, user):
    user_info = user_dao.find_by_tg_id(user.id)
    if user_info["a_list"]["url"] == "":
        bot.reply_to(message, open("templates/user_doesnt_have_a_list.html", encoding="utf-8").read()
                     .format(user.username))
        return
    bot.reply_to(message, open("templates/a_list_search_results.html", encoding="utf-8").read()
                 .format(user.username, user_info["a_list"]["url"]))


@bot.message_handler(commands=['clear_my_list'])
def delete_a_list(message):
    tg_id = message.from_user.id
    if not user_dao.is_registered(tg_id):
        bot.reply_to(message, open("templates/user_not_registered.html", encoding="utf-8").read())
        return
    if not user_dao.has_list(tg_id):
        bot.reply_to(message, open("templates/user_doesnt_have_a_list.html", encoding="utf-8").read()
                     .format("тебе"))
        return
    user_dao.modify_a_list(tg_id, "")
    bot.reply_to(message, open("templates/a_list_deletion_success.html", encoding="utf-8").read())


@bot.message_handler(commands=['show_lists'])
def show_a_lists(message):
    all_list_users = list(user_dao.get_all_with_a_list())
    if len(all_list_users) == 0:
        bot.reply_to(message, open("templates/a_lists_list_empty.html", encoding="utf-8").read())
        return
    output = ""
    for user in all_list_users:
        current_user = bot.get_chat_member(user["tg_id"], user["tg_id"]).user
        output += get_user_display_name(current_user) + "\n"
        output += "" + user["a_list"]["url"] + "\n\n"
    bot.reply_to(message, output)


def get_user_display_name(user):
    output = ""
    if user.first_name is not None:
        output += user.first_name + " "
    if user.last_name is not None:
        output += user.last_name + " "
    return output.strip()


"----------------------------------------------------------------------------"
"----------------------------ACHIEVEMENT COMMANDS----------------------------"
"----------------------------------------------------------------------------"


"/create_achievement Написати в гік-чат||Напиши будь що в нашу флудилку, https://t.me/geeKlubflood||100||1"


@bot.message_handler(commands=['create_achievement'])
def create_achievement(message):
    if message.from_user.username is None:
        bot.reply_to(message, open("templates/a_lists_list_empty.html", encoding="utf-8").read())
        return


"--------------------------------------------------------------"
"----------------------------SERVER----------------------------"
"--------------------------------------------------------------"


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
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
