import os  # noqa: D100

import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

load_dotenv()
token = os.getenv("TOKEN")

bot = telebot.TeleBot(token)

CAPTIONS = {
    "short": "🗣️ Короткая шутка",
    "people": "🙄 Ох уж эти люди…",  # noqa: RUF001,
    "food": "🍔 Анекдот про еду",
    "alco": "🥴 Анекдот про алкоголиков/наркоманов",
    "long": "👉 Длинный анекдот",
    "18+": "🔞 Анекдот для взрослых",
    "money": "💰 Шутка про деньги",
    "vovochka": "🤓 Анекдот про Вовочку",
    "animal": "🐹 Шутка про животных",
    "computer": "💻 Компьютерная шутка",
    "shtirlitz": "🪖 Шутка про Штирлица",
    "subscriber": "😛 Шутка от подписчика",
}


@bot.callback_query_handler(func=lambda _: True)
def handle_query(call: telebot.types.CallbackQuery) -> None:
    """Handle button's callback.

    Parameters
    ----------
    call : telebot.types.CallbackQuery
        the call

    Returns
    -------
    None

    """
    data = call.data.split(";")

    if data[0] == "anekdot.ru":
        send_anekdot_ru(call.message, int(data[1]))
        bot.answer_callback_query(call.id)
    if data[0].startswith("accept"):
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🗣", callback_data="short_joke"),
                        InlineKeyboardButton(text="🙄", callback_data="people_joke"),
                        InlineKeyboardButton(text="🍔", callback_data="food_joke"),
                        InlineKeyboardButton(text="🥴", callback_data="alco_joke"),
                        InlineKeyboardButton(text="👉", callback_data="long_joke"),
                        InlineKeyboardButton(text="🔞", callback_data="18+_joke"),
                    ],
                    [
                        InlineKeyboardButton(text="💰", callback_data="money_joke"),
                        InlineKeyboardButton(text="🤓", callback_data="vovochka_joke"),
                        InlineKeyboardButton(text="🐹", callback_data="animal_joke"),
                        InlineKeyboardButton(text="💻", callback_data="computer_joke"),
                        InlineKeyboardButton(text="🪖", callback_data="shtirlitz_joke"),
                        InlineKeyboardButton(
                            text="⬅",
                            callback_data=f"anekdot.ru;{data[0].split('$')[1]}",
                        ),
                    ],
                ],
            ),
        )
        bot.answer_callback_query(call.id)
    if data[0].endswith("_joke"):
        joke_type = data[0].split("_")[0]
        bot.edit_message_text(
            f"""*{CAPTIONS[joke_type]}*\n\n{'||' if joke_type == "18+" else ""}{call.message.text}{'||' if joke_type == "18+" else ""}""",  # noqa: E501
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
        )
        bot.answer_callback_query(call.id)


@bot.message_handler(commands=["start"])
def start(message: Message) -> None:
    """Start the jokes parsing.

    Parameters
    ----------
    message : telebot.types.Message
        message

    Returns
    -------
    None

    """
    bot.send_message(
        message.chat.id,
        "Выберите сайт, с которого хотите спарсить анекдоты 😂",  # noqa: RUF001,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="anekdot.ru",
                        callback_data="anekdot.ru;0",
                    ),
                ],
            ],
        ),
    )


def send_anekdot_ru(message: Message, n: int) -> None:
    """Send the joke from anekdot.ru website.

    Parameters
    ----------
    message : telebot.types.Message
        message
    n : int
        joke's index

    Returns
    -------
    None

    """
    try:
        url = "https://www.anekdot.ru/last/anekdot/"
        response = requests.get(url, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")
        jokes = [
            str(x)
            .replace('<div class="text">', "")
            .replace("</div>", "")
            .replace("<br/> ", "\n")
            .replace("<br/>", "\n")
            for x in soup.find_all("div", class_="text")
        ]

        bot.edit_message_text(
            jokes[n],
            message.chat.id,
            message.message_id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="✅", callback_data=f"accept${n}"),
                        InlineKeyboardButton(
                            text="➡",
                            callback_data=f"anekdot.ru;{n + 1}",
                        ),
                    ]
                    if n == 0
                    else [
                        InlineKeyboardButton(
                            text="⬅️",
                            callback_data=f"anekdot.ru;{n - 1}",
                        ),
                        InlineKeyboardButton(text="✅", callback_data=f"accept${n}"),
                        InlineKeyboardButton(
                            text="➡",
                            callback_data=f"anekdot.ru;{n + 1}",
                        ),
                    ],
                ],
            ),
        )
    except IndexError:
        bot.edit_message_text(
            "🙄 Шутки на сайте anekdot.ru закончились!",
            message.chat.id,
            message.message_id,
            reply_markup=None,
        )


@bot.message_handler(content_types=["text"])
def add_title(message: Message) -> None:
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(
        message.chat.id,
        message.text.replace(" anekdotov.net,", "").replace(
            " https://vse-shutochki.ru/anekdoty", ""
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🗣", callback_data="short_joke"),
                    InlineKeyboardButton(text="🙄", callback_data="people_joke"),
                    InlineKeyboardButton(text="🍔", callback_data="food_joke"),
                    InlineKeyboardButton(text="🥴", callback_data="alco_joke"),
                    InlineKeyboardButton(text="👉", callback_data="long_joke"),
                    InlineKeyboardButton(text="🔞", callback_data="18+_joke"),
                ],
                [
                    InlineKeyboardButton(text="💰", callback_data="money_joke"),
                    InlineKeyboardButton(text="🤓", callback_data="vovochka_joke"),
                    InlineKeyboardButton(text="🐹", callback_data="animal_joke"),
                    InlineKeyboardButton(text="💻", callback_data="computer_joke"),
                    InlineKeyboardButton(text="🪖", callback_data="shtirlitz_joke"),
                    InlineKeyboardButton(text="😛", callback_data="subscriber_joke"),
                ],
            ],
        ),
    )


bot.infinity_polling()
