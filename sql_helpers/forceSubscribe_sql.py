from pymongo import MongoClient
from Config import Config

# Configuración de la conexión a MongoDB
client = MongoClient(Config.MONGODB_URL)
db = client.get_database()

# Define la colección para 'forceSubscribe'
force_subscribe_collection = db.forceSubscribe

# Define la colección para 'Channel'
channel_collection = db.channel

def fs_settings(chat_id):
    try:
        # Intenta obtener las configuraciones relacionadas con el chat_id desde MongoDB
        return force_subscribe_collection.find_one({"chat_id": chat_id})
    except:
        return None

def add_channel(chat_id, channel):
    chat = force_subscribe_collection.find_one({"chat_id": chat_id})

    if chat:
        # Agrega el nuevo canal si no está presente
        channels = chat.get("channels", [])
        if channel not in channels:
            channels.append(channel)
            force_subscribe_collection.update_one(
                {"chat_id": chat_id},
                {"$set": {"channels": channels}}
            )
    else:
        # Si el chat_id no existe, crea un nuevo registro en MongoDB
        force_subscribe_collection.insert_one({"chat_id": chat_id, "channels": [channel]})

def disapprove(chat_id):
    # Elimina el registro asociado con el chat_id en MongoDB
    force_subscribe_collection.delete_one({"chat_id": chat_id})
