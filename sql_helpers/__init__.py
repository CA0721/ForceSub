import os
from pymongo import MongoClient
from Config import Config

# Configuración de la conexión a MongoDB
client = MongoClient(Config.MONGODB_URL)
db = client.get_database()

# Define la colección para 'forceSubscribe'
force_subscribe_collection = db.forceSubscribe

# Define la colección para 'Channel'
channel_collection = db.channel

def start():
    # No es necesario en MongoDB ya que no hay un equivalente directo a create_all
    pass

try:
    # No se necesita una declarative_base() en MongoDB
    SESSION = None
except AttributeError as e:
    print("MONGODB_URL is not configured. Features depending on the database might have issues.")
    print(str(e))
