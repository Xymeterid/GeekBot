import re

from db_acess_data import users


def find_by_tg_id(tg_id):
    return users.find_one({"tg_id": tg_id})


def is_registered(tg_id):
    return users.find_one({"tg_id": tg_id}) is not None


def has_list(tg_id):
    user_info = users.find_one({"tg_id": tg_id})
    return user_info["a_list"]["url"] != ""


def insert(tg_id):
    if find_by_tg_id(tg_id) is not None:
        return 0
    users.insert_one({
        "tg_id": tg_id,
        "obtained_achievements": [
            1
        ],
        "a_list": {
            "url": "",
            "type": "",
            "username": ""
        }
    })
    return 1


def modify_a_list(tg_id, list_link):
    if find_by_tg_id(tg_id) is None:
        return 0
    users.update_one({"tg_id": tg_id}, {"$set": {
            "a_list": {
                "url": list_link,
                "type": get_list_type(list_link),
                "username": get_list_username(list_link)
            }
        }})
    return 1


def get_list_username(list_url):
    list_type = get_list_type(list_url)
    if list_type == "anilist":
        username = re.sub("/animelist", "", re.sub("https://anilist\.co/user/", "", list_url))
    elif list_type == "myanimelist":
        username = re.sub("https://myanimelist\.net/animelist/", "", list_url)
    else:
        return None
    return username


def get_list_type(list_url):
    if re.search("anilist\.co/user/.+/animelist", list_url) is not None:
        return "anilist"
    if re.search("myanimelist\.net/animelist/.+", list_url) is not None:
        return "myanimelist"
    else:
        return None


def get_all():
    return users.find()


def get_all_with_a_list():
    query = {"a_list.url": {"$regex": "^https://"}}
    return users.find(query)


def delete(tg_id):
    return users.delete_one({"tg_id": tg_id})

