import logging
import time
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pymongo import MongoClient
from Config import Config, Messages as tr

logging.basicConfig(level=logging.INFO)

# Configuración de la conexión a MongoDB
client = MongoClient(Config.MONGODB_URL)
db = client.get_database()

# Define la colección para 'forceSubscribe'
force_subscribe_collection = db.forceSubscribe

@Client.on_message((filters.text | filters.media) & ~filters.private & ~filters.edited, group=1)
async def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = force_subscribe_collection.find_one({"chat_id": chat_id})

    if chat_db:
        user_id = message.from_user.id
        if not (await client.get_chat_member(chat_id, user_id)).status in ("administrator", "creator") and not user_id in Config.SUDO_USERS:
          channels = chat_db.get("channels", [])
          for channel in channels:
              try:
                  channel_info = await client.get_chat(channel)
                  channel_title = channel_info.title
                  await client.get_chat_member(channel, user_id)
              except UserNotParticipant:
                  try:
                      sent_message = await message.reply_text(
                          f"{message.from_user.mention}\n\nYou haven't joined our channel(s). "
                          f"Please join {channel_title} using the below button and press the UnMute Me button to unmute yourself.",
                          disable_web_page_preview=True,
                          reply_markup=InlineKeyboardMarkup(
                              [
                                  [
                                      InlineKeyboardButton(f"⚠️ Join {channel_title}", url=channel)
                                  ],
                                  [
                                      InlineKeyboardButton("✅ UnMute Me", callback_data="onUnMuteRequest")
                                  ]
                              ]
                          )
                      )
                      await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                  except ChatAdminRequired:
                      await sent_message.edit(f"❗ **I am not an admin in this chat or {channel_title}.**\n__Make me admin with ban user permission and add me again.\n#Leaving this chat...__")
                      await client.leave_chat(chat_id)
                  except Exception as e:
                      print(f"Error: {e}")

@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
async def config(client, message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.user.id in Config.SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1:]
            channels_added = []

            for channel_arg in input_str:
                channel = channel_arg.replace("@", "")
                try:
                    await client.get_chat_member(channel, "me")
                    force_subscribe_collection.update_one(
                        {"chat_id": chat_id},
                        {"$addToSet": {"channels": channel}},
                        upsert=True
                    )
                    channels_added.append(channel)
                except UserNotParticipant:
                    await message.reply_text(f"❗ **Not an Admin in the Channel**\n"
                                             f"__I am not an admin in the [channel]({channel}). Add me as admin in order to enable ForceSubscribe.__",
                                             disable_web_page_preview=True)
                except (UsernameNotOccupied, PeerIdInvalid):
                    await message.reply_text(f"❗ **Invalid Channel Username/ID: {channel}**")
                except Exception as err:
                    await message.reply_text(f"❗ **ERROR:** ```{err}```")

            if channels_added:
                channel_text = "\n".join([f"- `{channel}`" for channel in channels_added])
                await message.reply_text(f"✅ **Force Subscribe is Enabled**\n"
                                         f"__Force Subscribe is enabled for the following channel(s):\n{channel_text}__", disable_web_page_preview=True)
        else:
            chat_db = force_subscribe_collection.find_one({"chat_id": chat_id})
            if chat_db:
                channels = chat_db.get("channels", [])
                channel_text = "\n".join([f"- `{channel}`" for channel in channels])
                await message.reply_text(f"✅ **Force Subscribe is enabled in this chat.**\n"
                                         f"__For the following channel(s):\n{channel_text}__", disable_web_page_preview=True)
            else:
                await message.reply_text("❌ **Force Subscribe is disabled in this chat.**")
    else:
        await message.reply_text("❗ **Group Creator Required**\n__You have to be the group creator to do that.__")

