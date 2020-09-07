import requests
import dao.aliases_dao

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
    id
    description
    isAdult
  }
}
'''

anime_user_list_search_query = """
query ($userName: String, $titleId: Int) { 
  MediaList (userName: $userName, mediaId: $titleId){
    media{
      title{
        english
      }
    }
    score
  }
}
"""


def find_anime_in_users_anilist(title_id, username):
    return requests.post(url, json={'query': anime_user_list_search_query,
                                    'variables': {'userName': username, 'titleId': title_id}})


def find_anime_by_name_on_anilist(anime_name):
    if dao.aliases_dao.find(anime_name) is not None:
        anime_name = dao.aliases_dao.find(anime_name)["alias_value"]

    return requests.post(url, json={'query': anime_name_search_query, 'variables': {'search': anime_name}})
