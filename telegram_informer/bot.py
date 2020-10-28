import copy
import json
import uuid

from django.conf import settings
from django.db import transaction
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, \
    DispatcherHandlerStop

from database.models import ApprovedChat, TextContent, Accounts, OldPost
from painter.sova_timofei import SovaTimofeiPainter
from consumers.uploader import InstagramUploader
from promoting.statistic import get_stat

from .helpers import terminate_wrapper


class TgApprover():
    generated_source_name = 'generated'
    sova_timofei_username = 'sova_timofei'

    _instance = None

    class Registrator:
        commands = []
        callbacks = []

        @classmethod
        def command(cls, description):
            def decorator(method):
                cls.commands.append((terminate_wrapper(method), description))
                return method
            return decorator

        @classmethod
        def get_commands(cls):
            return cls.commands

        @classmethod
        def callback(cls, pattern):
            def decorator(method):
                cls.callbacks.append((terminate_wrapper(method), pattern))
                return method
            return decorator

        @classmethod
        def get_callbacks(cls):
            return cls.callbacks

    register_command = Registrator.command
    get_commands = Registrator.get_commands
    register_callback = Registrator.callback
    get_callbacks = Registrator.get_callbacks

    def __init__(self):
        self.updater = Updater(settings.TELEGRAM_BOT_ID)
        self.bot = Bot(settings.TELEGRAM_BOT_ID)
        self.dispatcher = self.updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(m.__name__, m) for m, _ in self.get_commands()],
            states={},
            fallbacks=[]
        )
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        for method, pattern in self.get_callbacks():
            self.dispatcher.add_handler(
                CallbackQueryHandler(method, pass_chat_data=True)
            )
        self.dispatcher.add_handler(conv_handler)
        self.dispatcher.add_handler(unknown_handler)
        self.dispatcher.add_error_handler(self.error)

    @staticmethod
    def _get_instance():
        if TgApprover._instance is None:
            TgApprover._instance = TgApprover()
        return TgApprover._instance

    @staticmethod
    @register_command("запуск")
    def start(bot, update):
        message = 'Добро пожаловать в АПРУВЕР, для списка команд наберите /help'
        bot.send_message(chat_id=update.message.chat_id, text=message)

    @staticmethod
    @register_command("помощь")
    def help(bot, update):
        message = 'Помощь:'
        message += ''.join([f'\n/{m.__name__} - {desc}' for (m, desc) in TgApprover.get_commands()])
        bot.send_message(chat_id=update.message.chat_id, text=message)

    @staticmethod
    @register_command("показать chat_id")
    def get_me(bot, update):
        message = f'Ваш chat id = {update.message.chat_id}'
        bot.send_message(chat_id=update.message.chat_id, text=message)

    @staticmethod
    @register_command("зарегистрировать для апрува")
    def register(bot, update):
        chat = update.message.chat_id
        if not ApprovedChat.objects.filter(chat=chat).exists():
            ApprovedChat.objects.create(chat=chat, enabled=True)
            message = f'Чат {chat} был добавлен в список для апрува.'
        else:
            message = f'Чат {chat} уже добавлен в список для апрува.'
        bot.send_message(chat_id=update.message.chat_id, text=message)

    @staticmethod
    @register_command("отменить регистрацию для апрува")
    def unregister(bot, update):
        chat = update.message.chat_id
        _, row_cnt = ApprovedChat.objects.filter(chat=chat).delete()
        if row_cnt[ApprovedChat._meta.label] > 0:
            message = f'Чат {chat} был удален из списка для апрува.'
        else:
            message = f'Чат {chat} не найден в списке для апрува.'
        bot.send_message(chat_id=update.message.chat_id, text=message)

    @staticmethod
    @register_command("показать статистику аккаунта")
    def ig_stat(bot, update):
        ig_account = update.message.text.replace('/ig_stat', '').strip()
        reply = get_stat(ig_account)
        bot.send_message(chat_id=update.message.chat_id, text=reply)

    @staticmethod
    @register_command("сгенерировать изображение")
    def generate_image(bot, update):
        text = update.message.text.replace('/generate_image', '').strip()
        onwer = Accounts.objects.get(username=TgApprover.sova_timofei_username)
        text_content = TextContent.objects.create(
            owner=onwer,
            parser_name=TgApprover.generated_source_name,
            text=text,
            post_id=uuid.uuid4(),
        )
        TgApprover.approve_text_content(text_content)

    @staticmethod
    def unknown(bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Неизвестна команда")

    @staticmethod
    @register_callback("approve_callback")
    def approve_callback(bot, update, chat_data):
        callback_query = update.callback_query
        operation_data = json.loads(callback_query.data)
        approved = operation_data['approved']
        text_content = TextContent.objects.get(pk=operation_data['text_content_id'])
        if text_content.instagram_post:
            callback_query.edit_message_text('Уже опубликовано')
            text_content.approved = True
            text_content.save()
            return
        send_to_upload_queue = False
        text_content.approved = approved
        text_content.save()
        if approved:
            uploader = InstagramUploader(text_content.owner)
            upload_queue_msg_count = uploader.get_message_count()
            if upload_queue_msg_count != 0:
                callback_query.edit_message_text(
                    f'В очереди {uploader.connector.queue} уже находятся сообщения (Кол-во = {upload_queue_msg_count}).'
                    f' Публикация отменена')
                return
            uploader.send_data(text_content)
            send_to_upload_queue = True
        text = 'Одобрено' + (' и отправлено на публикацию' if send_to_upload_queue else '') if approved else 'Неодобрено'
        callback_query.edit_message_text(text)

    @staticmethod
    @terminate_wrapper
    def error(bot, update, error):
        raise DispatcherHandlerStop(error)

    @staticmethod
    def approve_text_content(text_content: TextContent):
        instance = TgApprover._get_instance()
        image_path = text_content.draw(SovaTimofeiPainter())
        if image_path is None:
            return
        for approve_chat in ApprovedChat.objects.filter(enabled=True):
            callback_data = dict(
                approved=None,
                text_content_id=text_content.id,
            )
            callback_data_yes = copy.copy(callback_data)
            callback_data_yes['approved'] = True
            callback_data_no = copy.copy(callback_data)
            callback_data_no['approved'] = False
            if approve_chat:
                with open(image_path, 'rb') as image_file:
                    instance.bot.send_photo(approve_chat.chat, image_file)
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(('Да'), callback_data=json.dumps(callback_data_yes)),
                    InlineKeyboardButton(('Нет'), callback_data=json.dumps(callback_data_no)),
                ]])
                instance.bot.send_message(approve_chat.chat, 'Одобряем?', reply_markup=reply_markup)

    @staticmethod
    @transaction.atomic
    def approve_old_post(old_post: OldPost):
        instance = TgApprover._get_instance()
        owner = Accounts.objects.get(username=TgApprover.sova_timofei_username)
        text_content = TextContent.objects.create(
            owner=owner,
            parser_name=TgApprover.generated_source_name,
            text='-',
            post_id=uuid.uuid4(),
        )
        text_content.image = old_post.image_path
        text_content.save()
        old_post.text_content = text_content
        old_post.save()
        for approve_chat in ApprovedChat.objects.filter(enabled=True):
            callback_data = dict(
                approved=None,
                text_content_id=text_content.id,
            )
            callback_data_yes = copy.copy(callback_data)
            callback_data_yes['approved'] = True
            callback_data_no = copy.copy(callback_data)
            callback_data_no['approved'] = False
            if approve_chat:
                with open(old_post.image_path, 'rb') as image_file:
                    instance.bot.send_photo(approve_chat.chat, image_file)
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(('Да'), callback_data=json.dumps(callback_data_yes)),
                    InlineKeyboardButton(('Нет'), callback_data=json.dumps(callback_data_no)),
                ]])
                instance.bot.send_message(approve_chat.chat, 'Одобряем?', reply_markup=reply_markup)

    @staticmethod
    def run():
        instance = TgApprover._get_instance()
        instance.updater.start_polling()
        instance.updater.idle()
