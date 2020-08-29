import requests
import service.aliases_service

url = 'https://graphql.anilist.co'

anime_name_search_query = '''
query ($search: String) {
  Media (search: $search, type: ANIME) {
    title {
      romaji
      english
    }
    siteUrl
    idMal
    description
    isAdult
  }
}
'''

anime_name_search_reply_pattern = '''
<b>Назва:</b> {}
<b>Посилання:</b> <a href="{}">Anilist</a>|<a href="{}">MAL</a>
'''


def find_anime_by_name_on_anilist(anime_name):
    if service.aliases_service.find_alias(anime_name) is not None:
        anime_name = service.aliases_service.find_alias(anime_name)["alias_value"]

    response = requests.post(url, json={'query': anime_name_search_query, 'variables': {'search': anime_name}})

    if response.status_code == 200:

        json_response = (response.json())["data"]["Media"]

        if json_response['isAdult']:
            return "По моїй інформації цей тайтл має обмеження 18+. За правилами цього чату заборонено " \
                   "надсилати контент порнографічного характеру"

        if json_response['title']['english'] is None:
            display_name = json_response['title']['romaji']
        else:
            display_name = json_response['title']['english']

        return anime_name_search_reply_pattern.format(
                         display_name,
                         json_response['siteUrl'], "https://myanimelist.net/anime/{}".format(json_response["idMal"])
                     )
    else:
        return "Хм, схоже такого аніме не існує, або не вдається знайти нічого схожого. Спробуй інший запит. "
