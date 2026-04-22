import logging
import os

from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conversation states
# ---------------------------------------------------------------------------

GENDER, NAME, ORIGIN, AGE = range(4)  # Changed order to match logical flow

# ---------------------------------------------------------------------------
# Inline keyboard constants
# ---------------------------------------------------------------------------

NEXT_BUTTON = "next"
BACK_BUTTON = "back"
TUTORIAL_BUTTON = "tutorial"

FIRST_MENU_MARKUP = InlineKeyboardMarkup(
    [[InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)]]
)
SECOND_MENU_MARKUP = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
        [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")],
    ]
)

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Démarre la conversation et demande le genre."""
    reply_keyboard = [["Homme", "Femme", "Autre"]]

    await update.message.reply_text(
        "Je suis le robot d'Enrique. Puis-je echanger avec toi?\n"
        "Appuie sur /cancel si tu veux arrêter de discuter.\n\n"
        "Es-tu un homme ou une femme ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Homme, Femme ou Autre ?",
        ),
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enregistre le genre et demande le prénom."""
    user_gender = update.message.text
    context.user_data["gender"] = user_gender

    await update.message.reply_text(
        f"Merci ! Tu as choisi : {user_gender}\n\nMaintenant, quel est ton prénom ?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME  # Changed from AGE to NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enregistre le prénom et demande les origines."""
    user_name = update.message.text
    context.user_data["name"] = user_name

    await update.message.reply_text(f"Enchanté {user_name} ! Tu es de quelle origine ?")
    return ORIGIN


async def origin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enregistre l'origine et demande l'âge."""
    user_origin = update.message.text
    context.user_data["origin"] = user_origin
    
    # Check for specific origin
    if user_origin.lower() == "gwada":
        await update.message.reply_text("Ca ou fé ! 🌴")
    if user_origin.lower()== "france":
        await update.message.reply_text("bien le bonjour")
    if user_origin.lower() == "dz":
        await update.message.reply_text("Labes")
    
    await update.message.reply_text(f"Quel âge as-tu ?")
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enregistre l'âge et termine la conversation."""
    user_age = update.message.text
    context.user_data["age"] = user_age

    summary = (
        "Merci pour tes informations !\n"
        f"Prénom : {context.user_data.get('name')}\n"
        f"Genre  : {context.user_data.get('gender')}\n"
        f"Origine: {context.user_data.get('origin')}\n"
        f"Âge    : {user_age}\n\n"
        "Je te recontacterai bientôt !"
    )
    await update.message.reply_text(summary)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annule la conversation."""
    await update.message.reply_text(
        "Au revoir ! N'hésite pas à revenir discuter quand tu veux ! 👋"
    )
    return ConversationHandler.END


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Répercute les messages hors conversation."""
    logger.info("%s a écrit : %s", update.message.from_user.first_name, update.message.text)
    await update.message.copy(update.message.chat_id)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gère les clics sur les boutons inline."""
    query = update.callback_query
    await query.answer()

    if query.data == NEXT_BUTTON:
        await query.edit_message_text(
            "Tu as cliqué sur Suivant ! Voici le second menu :",
            reply_markup=SECOND_MENU_MARKUP,
        )
    elif query.data == BACK_BUTTON:
        await query.edit_message_text(
            "Retour au premier menu !",
            reply_markup=FIRST_MENU_MARKUP,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Variable d'environnement TELEGRAM_BOT_TOKEN manquante.")

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],  # Added NAME state
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, origin)],  # Added ORIGIN state
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
