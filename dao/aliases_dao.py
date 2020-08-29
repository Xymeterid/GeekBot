from db_acess_data import aliases


def find(alias_key):
    return aliases.find_one({"alias_key": alias_key})


def insert(alias_key, alias_value, user):
    if find(alias_key) is not None:
        aliases.update_one({"alias_key": alias_key}, {"$set": {
            "alias_key": alias_key,
            "alias_value": alias_value,
            "added_by": user
        }})
        return 2
    aliases.insert_one({
        "alias_key": alias_key,
        "alias_value": alias_value,
        "added_by": user})
    return 1


def get_all():
    return aliases.find()


def delete(alias_key):
    return aliases.delete_one({"alias_key": alias_key})

