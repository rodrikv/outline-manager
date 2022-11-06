#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import dotenv
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from outline_vpn.outline_vpn import OutlineVPN

from utils import group


dotenv.load_dotenv()

ADMIN = os.environ.get("admin", None)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.from_user.id)


async def register_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and int(ADMIN) != int(update.message.from_user.id):
        return

    commands = context.application.handlers.values()

    await update.message.reply_html(
        "\n".join(commands)
    )

async def get_servers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and int(ADMIN) != int(update.message.from_user.id):
        return

    commands = context.application.handlers.values()

    await update.message.reply_html(
        "\n".join(commands)
    )

async def get_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and int(ADMIN) != int(update.message.from_user.id):
        return

    keys = context.bot_data["outline"].get_keys()

    k_html = list(map(lambda x: f"{x.key_id}) <b>{x.name}</b>: <code>{x.access_url}</code>\n", keys))

    for i in group(k_html, 10):
        await update.message.reply_html(
            "\n".join(i)
        )

async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and int(ADMIN) != int(update.message.from_user.id):
        return

    name = update.message.text.split(maxsplit=1)[1]

    try:
        key = context.bot_data["outline"].create_key(name)
        await update.message.reply_html(
            f"Key <b>{key.name}</b> Created: <code>{key.access_url}</code>"
        )
    except:
        await update.message.reply_html(
            "Couldn't create the key!"
        )


async def delete_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and int(ADMIN) != int(update.message.from_user.id):
        return

    key_id: str = update.message.text.split(maxsplit=1)[1]

    if key_id.isnumeric():
        response = context.application.bot_data["outline"].delete_key(int(key_id))

        if response:
            await update.message.reply_html(
                f"Key ID <b>{key_id}</b> DELETED!"
            )
        else:
            await update.message.reply_html(
                f"Couldn't delete Key ID <b>{key_id}</b>!"
            )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["TOKEN"]).build()

    outline = OutlineVPN(os.environ["api_url"], cert_sha256=os.environ["certSha256"])

    application.bot_data["outline"] = outline

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("register_server", register_server))
    application.add_handler(CommandHandler("get_servers", get_servers))
    application.add_handler(CommandHandler("get_keys", get_keys))
    application.add_handler(CommandHandler("create_key", create_key))
    application.add_handler(CommandHandler("delete_key", delete_key))

    application.add_handler(CommandHandler("commands", commands))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
