import re
import telebot
import anilist_api_logic
import aliases_manager
from flask import Flask

TOKEN = "1364491220:AAE_T1pkCAiaaeq-fnNkzx1GyIzcfsCzgFQ"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

empty_anime_search_request = "Ця команда призначена для швидкого пошуку аніме. Натисни на кнопку" \
                      "\"відповісти\" на повідомленні з назвою щоб ініціювати пошук. Альтернативно, " \
                      "ти можеш виділити назву аніме в своєму повідомленні фігурними дужками, і пошук " \
                      "відбудеться автоматично, наприклад так: {Jojo}"

empty_alias_add_request = "Ця команда дозволяє додати сталу відповідність \"назва\"-\"аніме\". Це корисно якщо " \
                          "пошук за якоїсь причини не може знайти необхідний тайтл. Наприклад: \n\n" \
                          "/add_alias аріфурета == Arifureta: From Commonplace to World's Strongest \n\n" \
                          "Зверни увагу на пробіли біля дорівнює!"

empty_alias_delete_request = "Ця команда дозволяэ видалити alias. Наприклад: \n\n" \
                             "/delete_alias аріфурета"


@bot.message_handler(commands=['what_dis_uwu'])
def find_anime(message):

    if message.reply_to_message is None:
        anime_name = message.text.replace('/what_dis_uwu', '')
        if anime_name == '':
            bot.reply_to(message, empty_anime_search_request)
            return
    else:
        reply_text = message.reply_to_message.text
        name_found = re.search("{.+}", reply_text)
        if name_found is None:
            anime_name = reply_text
        else:
            anime_name = name_found.group()[1:-1]
    reply_message = anilist_api_logic.find_anime_by_name_on_anilist(anime_name.strip())
    bot.reply_to(message, reply_message, parse_mode="HTML")


@bot.message_handler(regexp="{.+}")
def find_anime_in_brackets(message):
    search_result = re.search("{.+}", message.text)
    anime_name = search_result.group()[1:-1]
    reply_message = anilist_api_logic.find_anime_by_name_on_anilist(anime_name.strip())
    bot.reply_to(message, reply_message, parse_mode="HTML")


@bot.message_handler(commands=['add_alias'])
def add_alias(message):
    message_text = message.text.replace('/add_alias', '')
    splits = message_text.split(" == ")
    if len(splits) < 2:
        bot.reply_to(message, empty_alias_add_request)
        return

    key = (splits[0]).strip().lower()
    value = (splits[1]).strip().lower()

    result = aliases_manager.add_alias(key, value)

    if result == 1:
        bot.reply_to(message, "Alias було успіно додано")
    if result == 0:
        bot.reply_to(message, "Alias вже існує, тому зміна не відбулась")


@bot.message_handler(commands=['show_aliases'])
def show_all_aliases(message):
    data = aliases_manager.get_all_aliases()
    if len(data) == 0:
        bot.reply_to(message, "Список alias наразі пустий")
    res = ""
    for key, value in data.items():
        res += "• " + key + " == " + value + "\n"
    bot.reply_to(message, res, parse_mode="HTML")


@bot.message_handler(commands=['delete_alias'])
def delete_alias(message):
    message_text = (message.text.replace('/delete_alias', '')).strip()
    if message_text == '':
        bot.reply_to(message, empty_alias_delete_request)
        return

    res = aliases_manager.delete_alias(message_text)
    if res == 1:
        bot.reply_to(message, "Alias було видалено")
    else:
        bot.reply_to(message, "Alias з таким ім'ям не існує")


"""
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
    """

if __name__ == "__main__":
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=0)
