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

def find_anime_by_name_on_anilist(anime_name):
    if service.aliases_service.find_alias(anime_name) is not None:
        anime_name = service.aliases_service.find_alias(anime_name)["alias_value"]

    return requests.post(url, json={'query': anime_name_search_query, 'variables': {'search': anime_name}})
