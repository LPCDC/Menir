import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from src.v3.menir_runner import MenirRunner
from src.v3.tenant_middleware import current_tenant_id

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("MenirTelegram")

load_dotenv(override=True)

# Security: Only this Telegram User ID is allowed to talk to the bot.
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Runner dependencies silently
runner = MenirRunner(project_name="Telegram_Inbox")
runner.initialize_services()

async def auth_check(update: Update) -> bool:
    """Security Gate: Rejects unauthorized users silently."""
    chat_id = str(update.effective_chat.id)
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        logger.warning(f"Unauthorized access attempt from Chat ID: {chat_id}")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update): return
    
    welcome_msg = (
        "🧠 *Menir Brain Online.*\n"
        "Aguardando instruções. Você pode me mandar textos, ideias ou áudios. "
        "Eu extrairei a ontologia (Eventos/Conceitos/Tempo) e salvarei no Grafo Neo4j."
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Utility command so the user can discover their Chat ID for the .env file."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Seu Chat ID é: `{chat_id}`", parse_mode='Markdown')

async def process_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update): return
    
    text = update.message.text
    message_id = str(update.message.message_id) # Using message ID as a pseudo hash
    logger.info(f"Received Telegram Text: {text[:50]}...")
    
    await update.message.reply_text("Processando no motor cognitivo... ⏳")
    
    try:
        # Extract Knowledge using Intel (Gemini)
        extraction = runner.intel.extract(text, "Telegram_Inbox", message_id)
        
        # Write to Neo4j Securely
        token = current_tenant_id.set("root_admin")
        try:
            runner.ingest_payload(extraction, "Telegram_Inbox", message_id)
        finally:
            current_tenant_id.reset(token)
            
        # Count what was saved
        nodes_count = len(extraction.get("nodes", []))
        edges_count = len(extraction.get("edges", []))
        
        reply = f"✅ *Memória Injetada no Grafo!*\n- {nodes_count} Nós Extraídos\n- {edges_count} Relações Mapeadas."
        await update.message.reply_text(reply, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Failed to process Telegram message: {e}")
        await update.message.reply_text(f"❌ *Erro de Extração:* {str(e)}", parse_mode='Markdown')

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN is missing from .env!")
        return

    application = ApplicationBuilder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", get_my_id))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_text_message))

    # Start polling
    logger.info("📡 Menir Telegram Gateway Active. Polling for messages...")
    application.run_polling()

if __name__ == '__main__':
    main()
