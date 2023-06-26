import asyncio
from datetime import timedelta

import telegram
from django.utils.timezone import localtime

from Library_Service_API import settings

from celery import shared_task

from borrowings.models import Borrowing


def format_datetime(datetime_obj):
    return localtime(datetime_obj).strftime("%Y-%m-%d")


async def send_telegram_message(bot_token, chat_id, message):
    bot = telegram.Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)


@shared_task
def send_telegram_notification(borrowing_id):
    borrowing = Borrowing.objects.get(id=borrowing_id)
    borrow_date = format_datetime(borrowing.borrow_date)
    expected_return_date = format_datetime(borrowing.expected_return_date)
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    message = (
        f"New borrowing: \n"
        f"Book: {borrowing.book.title}\n"
        f"User: {borrowing.user.email}\n"
        f"Borrow Date: {borrow_date}\n"
        f"Expected Return Date: {expected_return_date}")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_telegram_message(bot_token, chat_id, message))


@shared_task
def send_notification_about_overdue_borrowings():
    tomorrow = localtime() + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow, actual_return_date__isnull=True
    )
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            borrow_date = format_datetime(borrowing.borrow_date)
            expected_return_date = format_datetime(borrowing.expected_return_date)

            message = (
                f"Overdue borrowing:\n"
                f"Book: {borrowing.book.title}\n"
                f"User: {borrowing.user.email}\n"
                f"Borrow Date: {borrow_date}\n"
                f"Expected Return Date: {expected_return_date}"
            )
            asyncio.run(send_telegram_message(bot_token, chat_id, message))

    else:
        message = "No borrowings overdue today!"
        asyncio.run(send_telegram_message(bot_token, chat_id, message))
