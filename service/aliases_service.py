import dao.aliases_dao


def find_alias(alias_key):
    return dao.aliases_dao.find(alias_key)


def get_all_aliases():
    return dao.aliases_dao.get_all()


def insert_alias(alias_key, alias_value, user):
    return dao.aliases_dao.insert(alias_key, alias_value, user)


def delete_alias(alias_key):
    return dao.aliases_dao.delete(alias_key)

