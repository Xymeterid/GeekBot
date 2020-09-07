import pymongo

client = pymongo.MongoClient('mongodb+srv://Xymeterid:007agent007@cluster0.qxfxh.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = client.main_db
aliases = db.aliases
users = db.users
