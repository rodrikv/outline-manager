import os
import dotenv
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from outline_vpn.outline_vpn import OutlineVPN

from utils import convert_size, group


dotenv.load_dotenv()

ADMIN = os.environ.get("admins", None)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(update.message.from_user.id)


async def register_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and str(update.message.from_user.id) not in ADMIN:
        return

    commands = context.application.handlers.values()

    await update.message.reply_html("\n".join(commands))


async def get_servers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and str(update.message.from_user.id) not in ADMIN:
        return

    commands = context.application.handlers.values()

    await update.message.reply_html("\n".join(commands))


async def get_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and str(update.message.from_user.id) not in ADMIN:
        return

    keys = context.bot_data["outline"].get_keys()

    k_html = list(
        map(
            lambda x: f"{x.key_id}) <b>{x.name}</b> ({convert_size(x.used_bytes)}) : <code>{x.access_url}</code>\n",
            keys,
        )
    )

    for i in group(k_html, 10):
        await update.message.reply_html(
            "\n".join([f"Total Keys Created: {len(k_html)}", ""] + i)
        )


async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and str(update.message.from_user.id) not in ADMIN:
        return

    name = update.message.text.split(maxsplit=1)[1]

    try:
        key = context.bot_data["outline"].create_key(name)
        await update.message.reply_html(
            f"Key <b>{key.name}</b> Created: <code>{key.access_url}</code>"
        )
    except:
        await update.message.reply_html("Couldn't create the key!")


async def delete_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if ADMIN is not None and str(update.message.from_user.id) not in ADMIN:
        return

    key_id: str = update.message.text.split(maxsplit=1)[1]

    if key_id.isnumeric():
        response = context.application.bot_data["outline"].delete_key(int(key_id))

        if response:
            await update.message.reply_html(f"Key ID <b>{key_id}</b> DELETED!")
        else:
            await update.message.reply_html(f"Couldn't delete Key ID <b>{key_id}</b>!")


async def get_server_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    outline: OutlineVPN = context.application.bot_data["outline"]
    info = outline.get_server_information()
    logger.info(info)

    await update.message.reply_html(
        "\n".join(f"<b>{key}</b>: <pre>{value}</pre>" for key, value in info.items())
    )


async def rename_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    outline: OutlineVPN = context.application.bot_data["outline"]

    _, key_id, name = update.message.text.split(maxsplit=2)

    if key_id.isnumeric():
        key_id = int(key_id)
    else:
        return await update.message.reply_html("Key ID must be integer and valid!")

    response = outline.rename_key(key_id, name)

    if response:
        await update.message.reply_html(
            f"Key ID <b>{key_id}</b> renamed to -> <b>{name}</b>"
        )
    else:
        await update.message.reply_html(f"Couldn't rename!")


async def get_transferred_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    outline: OutlineVPN = context.application.bot_data["outline"]

    try:
        data = outline.get_transferred_data()
        logger.info(data)
        await update.message.reply_html(
            f"Total Transferred Data: <b>{convert_size(sum(data['bytesTransferredByUserId'].values()))}</b>"
        )
    except Exception as e:
        logger.warning(e)
        await update.message.reply_html(f"Error Occured!")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["TOKEN"]).build()

    outline = OutlineVPN(os.environ["api_url"], cert_sha256=os.environ["certSha256"])

    application.bot_data["outline"] = outline

    application.add_handler(CommandHandler("register_server", register_server))
    application.add_handler(CommandHandler("get_servers", get_servers))
    application.add_handler(CommandHandler("get_keys", get_keys))
    application.add_handler(CommandHandler("create_key", create_key))
    application.add_handler(CommandHandler("delete_key", delete_key))
    application.add_handler(CommandHandler("get_server_info", get_server_info))
    application.add_handler(CommandHandler("rename_key", rename_key))
    application.add_handler(
        CommandHandler("get_transferred_data", get_transferred_data)
    )

    application.add_handler(CommandHandler("commands", commands))

    application.run_polling()


if __name__ == "__main__":
    main()
