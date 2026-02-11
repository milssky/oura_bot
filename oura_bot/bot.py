import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from oura_bot.provider import container
from oura_bot.repository import TPRepository
from oura_bot.tasks import pull_and_send_task

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command."""
    if str(update.effective_chat.id) != os.environ.get('ADMIN_TG_CHAT_ID'):
        return
    await update.message.reply_text(
        'Admin bot is running.\n'
        'Available commands:\n'
        '/start - Show this message\n'
        '/pull - Trigger manual data pull\n'
        '/set_tp_token <token> - Set TrainingPeaks token\n'
        '/add_tp_user <name> <athlete_id> - Add TrainingPeaks user'
    )


async def set_tp_token(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Set TP token command."""
    if str(update.effective_chat.id) != os.environ.get('ADMIN_TG_CHAT_ID'):
        return

    if not context.args:
        await update.message.reply_text('Usage: /set_tp_token <token>')
        return

    token = context.args[0]
    tp_repo = container.get(TPRepository)
    await tp_repo.update_token(token)
    await update.message.reply_text('TrainingPeaks token updated successfully.')


async def add_tp_user(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Add TP user command."""
    if str(update.effective_chat.id) != os.environ.get('ADMIN_TG_CHAT_ID'):
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            'Usage: /add_tp_user <name> <athlete_id>'
        )
        return

    name = context.args[0]
    try:
        athlete_id = int(context.args[1])
    except ValueError:
        await update.message.reply_text('athlete_id must be an integer.')
        return

    tp_repo = container.get(TPRepository)
    await tp_repo.add_user(name=name, athlete_id=athlete_id)
    await update.message.reply_text(
        f'User {name} with athlete_id {athlete_id} added.'
    )


async def trigger_pull(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Trigger manual data pull."""
    if str(update.effective_chat.id) != os.environ.get('ADMIN_TG_CHAT_ID'):
        return
    await update.message.reply_text('Triggering manual pull...')
    await pull_and_send_task()
    await update.message.reply_text('Manual pull completed.')


def get_bot_app() -> Application:
    """Build bot application."""
    token = os.environ.get('BOT_TOKEN')
    if not token:
        raise ValueError('BOT_TOKEN environment variable is not set')

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('pull', trigger_pull))
    app.add_handler(CommandHandler('set_tp_token', set_tp_token))
    app.add_handler(CommandHandler('add_tp_user', add_tp_user))
    return app
