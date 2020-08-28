import json

with open('res/aliases.json') as json_file:
    data = json.load(json_file)


def add_alias(key, value):
    if key in data:
        return 0
    else:
        data[key] = value
        with open('res/aliases.json', 'w') as outfile:
            json.dump(data, outfile)
        return 1


def alias_exists(key):
    if key in data:
        return True
    else:
        return False


def get_alias(key):
    return data[key]


def get_all_aliases():
    return data


def delete_alias(key):
    if key in data:
        del data[key]
        return 1
    else:
        return 0
