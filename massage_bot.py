import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputMediaPhoto
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import os

import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT
)
""")
conn.commit()


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = list(map(int, os.getenv("ADMINS").split(",")))

print("🔥 VERSION 2 LOADED")

MANAGER = "https://t.me/Lenmaxsym"
MAP_URL = "https://maps.apple/p/sF_AhaQ4n170BQ"

session = AiohttpSession(timeout=60)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

# ⚠️ МОВА ЗБЕРІГАЄТЬСЯ ТІЛЬКИ В СЕСІЇ
users_lang = {}


# ---------- STATES ----------
class Broadcast(StatesGroup):
    waiting = State()


class PhotoUpdate(StatesGroup):
    waiting = State()


class AboutPhotoUpdate(StatesGroup):
    waiting_photo = State()


# ---------- TEXTS ----------
TEXTS = {
    "ua": {
        "lang": "🌍 Оберіть мову",
        "welcome": "🌿 Ласкаво просимо до нашого масажного салону",
        "menu": {
            "services": "💆‍♀️ Послуги",
            "masters": "👩 Наші майстри",
            "location": "📍 Як нас знайти",
            "about": "🏠 Про салон",
        },
        "back": "🔙 Повернутись",
        "book": "📩 Записатись",
        "location_text": (
            "📍 Адреса: R. Pedro Reinel 16, Cascais, квартира 3B\n\n"
            "📞 Телефон: +351 967 605 926\n"
            "✉️ Email: Olenamaksymchuk880@gmail.com\n\n"
            "🕘 Часи роботи: 9:30 – 17:00"
        ),
        "about_text": (
            "Наш салон — це простір турботи, гармонії та відновлення 🌿✨\n\n"
            "Тут ви можете зупинитись, розслабитись і повністю присвятити час собі 💆‍♀️\n\n"
            "Ми поєднуємо професійні масажні техніки та сучасні апаратні процедури, "
            "працюючи з тілом комплексно та делікатно 🤍\n\n"
            "Кожна процедура підбирається індивідуально, відповідно до ваших потреб, "
            "самопочуття та бажаного результату 🌸"
        ),
        "open_map": "🗺 Відкрити на карті",
        "choose_category": "Оберіть категорію",
        "choose_service": "Оберіть послугу",
        "choose_master": "Оберіть майстра",
        "admin": "🔐 Адмін панель",
        "broadcast": "📢 Розсилка",
        "stats": "📊 Статистика",
        "enter_broadcast": "✏️ Надішліть текст або фото з текстом",
        "users": "👥 Користувачів",
    },
    "ru": {
        "lang": "🌍 Выберите язык",
        "welcome": "🌿 Добро пожаловать в наш массажный салон",
        "menu": {
            "services": "💆‍♀️ Услуги",
            "masters": "👩 Наши мастера",
            "location": "📍 Как нас найти",
            "about": "🏠 О салоне",
        },
        "back": "🔙 Назад",
        "book": "📩 Записаться",
        "location_text": (
            "📍 Адрес: R. Pedro Reinel 16, Cascais, квартира 3B\n\n"
            "📞 Телефон: +351 967 605 926\n"
            "✉️ Email: Olenamaksymchuk880@gmail.com\n\n"
            "🕘 Время работы: 9:30 – 17:00"
        ),
        "about_text": (
            "Наш салон — это пространство заботы, уюта и восстановления 🌿✨\n\n"
            "Здесь вы можете остановиться, расслабиться и посвятить время только себе 💆‍♀️\n\n"
            "Мы объединяем профессиональные массажные техники и современные аппаратные процедуры, "
            "работая с телом комплексно и бережно 🤍\n\n"
            "Каждая процедура подбирается индивидуально — с учётом ваших потребностей, "
            "самочувствия и желаемого результата 🌸"
        ),
        "open_map": "🗺 Открыть на карте",
        "choose_category": "Выберите категорию",
        "choose_service": "Выберите услугу",
        "choose_master": "Выберите мастера",
        "admin": "🔐 Админ панель",
        "broadcast": "📢 Рассылка",
        "stats": "📊 Статистика",
        "enter_broadcast": "✏️ Отправьте текст или фото с текстом",
        "users": "👥 Пользователей",
    },
    "pt": {
        "lang": "🌍 Escolha o idioma",
        "welcome": "🌿 Bem-vindo ao nosso salão de massagens",
        "menu": {
            "services": "💆‍♀️ Serviços",
            "masters": "👩 Nossos especialistas",
            "location": "📍 Como nos encontrar",
            "about": "🏠 Sobre o salão",
        },
        "back": "🔙 Voltar",
        "book": "📩 Marcar",
        "location_text": (
            "📍 Endereço: R. Pedro Reinel 16, Cascais, apartamento 3B\n\n"
            "📞 Telefone: +351 967 605 926\n"
            "✉️ Email: Olenamaksymchuk880@gmail.com\n\n"
            "🕘 Horário: 9:30 – 17:00"
        ),
        "about_text": (
            "O nosso salão é um espaço de cuidado, conforto e renovação 🌿✨\n\n"
            "Aqui você pode desacelerar, relaxar e dedicar um tempo só para si 💆‍♀️\n\n"
            "Combinamos técnicas profissionais de massagem com procedimentos estéticos modernos, "
            "trabalhando o corpo de forma completa e cuidadosa 🤍\n\n"
            "Cada tratamento é escolhido individualmente, de acordo com as suas necessidades, "
            "bem-estar e objetivos desejados 🌸"
        ),
        "open_map": "🗺 Abrir no mapa",
        "choose_category": "Escolha a categoria",
        "choose_service": "Escolha o serviço",
        "choose_master": "Escolha o especialista",
        "admin": "🔐 Painel administrativo",
        "broadcast": "📢 Envio",
        "stats": "📊 Estatísticas",
        "enter_broadcast": "✏️ Envie texto ou foto com texto",
        "users": "👥 Usuários",
    },
}

# ---------- SERVICES ----------
SERVICES = {
    "ua": {
        "Комплекси": {
            "combo1": (
                "Обгортування(50€) + прессотерапія(35€) + масаж(2 руки - 70€, 4 руки - 90€)\n\n"
                "⏱ 1 год 40 хв\n\n"
                "Одноразовий:\n"
                "💶 2 руки — 155€ | 4 руки — 175€\n\n"
                "Курси:\n"
                "2 руки - 5 сеансів — 750€\n"
                "           10 сеансів — 1450€\n"
                "4 руки - 5 сеансів — 850€\n"
                "           10 сеансів — 1650€\n"
            )
        },
        "Масажі": {
            "body": (
                "Масаж всього тіла + банки\n\n"
                "💶 70€\n\n"
                "Курс:\n"
                "5 сеансів — 325€\n"
                "10 сеансів — 600€"
            ),
            "face": (
                "Масаж обличчя\n\n" "30 хв — 40€\n" "1 год — 65€\n" "Курс 5 — 300€"
            ),
            "four": ("Масаж 4 руки\n\n" "1 раз — 90€\n" "Курс 5 — 425 €  "),
        },
        "Обгортання": {
            "lipofit": "Lipofit (живіт) — 175€",
            "firming": "Firming (руки + живіт + ноги) — 285€",
            "nio": "Nio Drain — 190€",
            "fobro": "Fobrocel — 200€",
            "cel": "Cel Term — 4 сеанси - 150€",
            "crio": "Crio Tonic — 4 сеанси - 150€ ",
            "detoxy": "Detoxy — 4 сеанси  - 220€",
        },
        "RF": {
            "combo": ("Комбо масаж + обгортання + RF\n" "⏱ 1:30\n" "💶 115€ - один"),
            "rf": ("RF по зонах\n" "30 хв — 55€\n" "Курс з 8 — 440€"),
        },
        "Скраби": {"arosha": ("Скраб Arosha\n\n" "⏱ 30 хв\n\n" "💶 25€")},
    },
    "ru": {
        "Комплексы": {
            "combo1": (
                "Обертывание (50€) + прессотерапия (35€) + массаж "
                "(2 руки — 70€, 4 руки — 90€)\n\n"
                "⏱ 1 час 40 мин\n\n"
                "Разовый сеанс:\n"
                "💶 2 руки — 155€ | 4 руки — 175€\n\n"
                "Курсы:\n"
                "2 руки — 5 сеансов — 750€\n"
                "           10 сеансов — 1450€\n"
                "4 руки — 5 сеансов — 850€\n"
                "           10 сеансов — 1650€\n"
            )
        },
        "Массажи": {
            "body": (
                "Массаж всего тела + банки\n\n"
                "💶 70€\n\n"
                "Курс:\n"
                "5 сеансов — 325€\n"
                "10 сеансов — 600€"
            ),
            "face": ("Массаж лица\n\n" "30 мин — 40€\n" "1 ч — 65€\n" "Курс 5 — 300€"),
            "four": ("Массаж 4 руки\n\n" "1 раз — 90€\n" "Курс 5 — 425€"),
        },
        "Обертывания": {
            "lipofit": "Lipofit (живот) — 175€",
            "firming": "Firming (руки + живот + ноги) — 285€",
            "nio": "Nio Drain — 190€",
            "fobro": "Fobrocel — 200€",
            "cel": "Cel Term — 4 сеанси - 150€",
            "crio": "Crio Tonic — 4 сеанси - 150€",
            "detoxy": "Detoxy — 4 сеанси - 220€",
        },
        "RF": {
            "combo": ("Комбо массаж + обертывание + RF\n" "⏱ 1:30\n" "💶 115€ за один"),
            "rf": ("RF по зонам\n" "30 мин — 55€\n" "Курс 8 — 220€"),
        },
        "Скрабы": {"arosha": ("Скраб Arosha\n\n" "⏱ 30 мин\n\n" "💶 25€")},
    },
    "pt": {
        "Combos": {
            "combo1": (
                "Envolvimento corporal (50€) + pressoterapia (35€) + massagem "
                "(2 mãos — 70€, 4 mãos — 90€)\n\n"
                "⏱ 1h 40min\n\n"
                "Sessão única:\n"
                "💶 2 mãos — 155€ | 4 mãos — 175€\n\n"
                "Pacotes:\n"
                "2 mãos — 5 sessões — 750€\n"
                "           10 sessões — 1450€\n"
                "4 mãos — 5 sessões — 850€\n"
                "           10 sessões — 1650€\n"
            )
        },
        "Massagens": {
            "body": (
                "Massagem de corpo inteiro + ventosas\n\n"
                "💶 70€\n\n"
                "Pacote:\n"
                "5 sessões — 325€\n"
                "10 sessões — 600€"
            ),
            "face": (
                "Massagem facial\n\n" "30 min — 40€\n" "1 h — 65€\n" "Pacote 5 — 300€"
            ),
            "four": ("Massagem 4 mãos\n\n" "1 sessão — 90€\n" "Pacote 5 — 425€ "),
        },
        "Envolvimentos": {
            "lipofit": "Lipofit (abdómen) — 175€",
            "firming": "Firming (braços + abdómen + pernas) — 285€",
            "nio": "Nio Drain — 190€",
            "fobro": "Fobrocel — 200€",
            "cel": "Cel Term — 4 sessões - 150€",
            "crio": "Crio Tonic — 4 sessões - 150€",
            "detoxy": "Detoxy — 4 sessões - 220€",
        },
        "RF": {
            "combo": ("Massagem + envolvimento + RF\n" "⏱ 1:30\n" "💶 115€"),
            "rf": ("RF por zonas\n" "30 min — 55€\n" "Pacote 8 — 440€"),
        },
        "Esfoliação": {"arosha": ("Esfoliação Arosha\n\n" "⏱ 30 min\n\n" "💶 25€")},
    },
}

# ---------- MASTERS ----------
MASTERS = {
    "ua": {
        "Ольга": (
            "🌿 Ольга — майстриня баночного масажу 🌿\n\n"
            "Мʼякий та уважний підхід до кожного клієнта 💆‍♀️\n\n"
            "Відчуття турботи та тепла з першого дотику.\n\n"
            "✨ Чому варто спробувати:\n"
            "• активний лімфодренаж — зменшення набряків та важкості\n"
            "• покращення циркуляції крові\n"
            "• розслаблення мʼязів і зняття спазмів\n"
            "• згладження рельєфу шкіри та зменшення целюліту\n"
            "• результат вже після перших сеансів\n\n"
            "💖 Ольга дарує відчуття легкості, краси та гарного настрою"
        ),
        "Олена": (
            "💆‍♀️ Олена — терапевтичний масаж\n\n"
            "13 років досвіду у фізіотерапії та терапевтичному масажі.\n\n"
            "Ви можете довіритися професіоналу, який дбає про ваше тіло та здоровʼя.\n\n"
            "✨ Показання та ефект:\n"
            "• біль у спині, шиї або попереку\n"
            "• перенапруження після роботи чи тренувань\n"
            "• обмеження рухливості та наслідки травм\n"
            "• хронічна втома та стрес\n\n"
            "✔ глибока робота з мʼязами та фасціями\n"
            "✔ покращення кровообігу та рухливості\n"
            "✔ мʼяке зняття болю та спазмів\n"
            "✔ повне відновлення після навантажень"
        ),
        "Галя": (
            "🌸 Галя — релакс масаж 😌\n\n"
            "Ніжний дотик та повне розслаблення.\n"
            "Ідеально для тих, хто хоче відпочити від стресу та метушні.\n\n"
            "✨ Переваги:\n"
            "• глибоке розслаблення мʼязів\n"
            "• зняття напруги та стресу\n"
            "• легкість у тілі та голові\n"
            "• покращення кровообігу та самопочуття\n"
            "• відновлення енергії і гарного настрою\n\n"
            "💖 Кожен сеанс з Галею — маленький ритуал турботи про себе"
        ),
    },
    "ru": {
        "Ольга": (
            "🌿 Ольга — мастер баночного массажа 🌿\n\n"
            "Мягкий и внимательный подход к каждому клиенту 💆‍♀️\n\n"
            "Чувство заботы и тепла с первого прикосновения.\n\n"
            "✨ Почему стоит попробовать:\n"
            "• активный лимфодренаж — уменьшение отеков и тяжести\n"
            "• улучшение кровообращения\n"
            "• расслабление мышц и снятие спазмов\n"
            "• сглаживание рельефа кожи и уменьшение целлюлита\n"
            "• заметный результат уже после первых сеансов\n\n"
            "💖 Ольга дарит ощущение легкости, красоты и отличного настроения"
        ),
        "Елена": (
            "💆‍♀️ Елена — терапевтический массаж\n\n"
            "13 лет опыта в физиотерапии и терапевтическом массаже.\n\n"
            "Вы можете довериться профессионалу, который заботится о вашем теле и здоровье.\n\n"
            "✨ Показания и эффекты:\n"
            "• боли в спине, шее или пояснице\n"
            "• перенапряжение после работы или тренировок\n"
            "• ограничение подвижности и последствия травм\n"
            "• хроническая усталость и стресс\n\n"
            "✔ глубокая работа с мышцами и фасциями\n"
            "✔ улучшение кровообращения и подвижности\n"
            "✔ мягкое снятие боли и спазмов\n"
            "✔ полное восстановление после нагрузок"
        ),
        "Галя": (
            "🌸 Галя — релакс массаж 😌\n\n"
            "Нежное прикосновение и полное расслабление.\n"
            "Идеально для тех, кто хочет отдохнуть от стресса и суеты.\n\n"
            "✨ Преимущества:\n"
            "• глубокое расслабление мышц\n"
            "• снятие напряжения и стресса\n"
            "• легкость в теле и голове\n"
            "• улучшение кровообращения и самочувствия\n"
            "• восстановление энергии и хорошего настроения\n\n"
            "💖 Каждый сеанс с Галей — маленький ритуал заботы о себе"
        ),
    },
    "pt": {
        "Olga": (
            "🌿 Olga — massagem com ventosas 🌿\n\n"
            "Toque suave e atenção especial 💆‍♀️\n\n"
            "✨ Benefícios:\n"
            "• drenagem linfática — redução de inchaços e sensação de peso\n"
            "• melhora da circulação sanguínea\n"
            "• relaxamento muscular e alívio de tensões\n"
            "• pele mais lisa e tonificada\n"
            "• resultados perceptíveis desde a primeira sessão\n\n"
            "💖 Olga proporciona leveza, beleza e bem-estar"
        ),
        "Elena": (
            "💆‍♀️ Olena — massagem terapêutica\n\n"
            "13 anos de experiência em fisioterapia e massagem terapêutica.\n\n"
            "Confie em uma profissional que cuida do seu corpo e bem-estar.\n\n"
            "✨ Indicações e efeitos:\n"
            "• dores nas costas, pescoço ou lombar\n"
            "• tensão após trabalho ou exercícios\n"
            "• limitação de movimentos e consequências de lesões\n"
            "• fadiga crônica e estresse\n\n"
            "✔ trabalho profundo com músculos e fáscias\n"
            "✔ melhora da circulação e mobilidade\n"
            "✔ alívio suave da dor e espasmos\n"
            "✔ recuperação completa após esforços físicos"
        ),
        "Galya": (
            "🌸 Halya — massagem relaxante 😌\n\n"
            "Toque delicado e relaxamento profundo.\n"
            "Ideal para quem quer descansar do estresse e da correria.\n\n"
            "✨ Benefícios:\n"
            "• relaxamento muscular profundo\n"
            "• alívio de tensão e estresse\n"
            "• leveza no corpo e mente\n"
            "• melhora da circulação e bem-estar\n"
            "• renovação de energia e bom humor\n\n"
            "💖 Cada sessão com Halya é um pequeno ritual de cuidado consigo mesmo"
        ),
    },
}

MASTERS_PHOTOS = {
    "ua": {
        "Ольга": "AgACAgIAAxkBAAIDNWlSk9KgJ2VN2nzrHPTVBDXS2RRGAALyEWsbwVKRShhJVL_CxfTJAQADAgADeQADNgQ",
        "Олена": "AgACAgIAAxkBAAIDY2lS2WaxA-bmLL-SvdLCpIv3iyEGAAJiDWsbwVKZSjqH4kpaqwSTAQADAgADeQADNgQ",
        "Галя": "AgACAgIAAxkBAAIDZmlS2W63NbaEJt3WgGbQRimPIxhLAAJjDWsbwVKZSkUcFQRdAXGiAQADAgADeQADNgQ",
    },
    "ru": {
        "Ольга": "AgACAgIAAxkBAAIDNWlSk9KgJ2VN2nzrHPTVBDXS2RRGAALyEWsbwVKRShhJVL_CxfTJAQADAgADeQADNgQ",
        "Елена": "AgACAgIAAxkBAAIDY2lS2WaxA-bmLL-SvdLCpIv3iyEGAAJiDWsbwVKZSjqH4kpaqwSTAQADAgADeQADNgQ",
        "Галя": "AgACAgIAAxkBAAIDZmlS2W63NbaEJt3WgGbQRimPIxhLAAJjDWsbwVKZSkUcFQRdAXGiAQADAgADeQADNgQ",
    },
    "pt": {
        "Olga": "AgACAgIAAxkBAAIDNWlSk9KgJ2VN2nzrHPTVBDXS2RRGAALyEWsbwVKRShhJVL_CxfTJAQADAgADeQADNgQ",
        "Elena": "AgACAgIAAxkBAAIDY2lS2WaxA-bmLL-SvdLCpIv3iyEGAAJiDWsbwVKZSjqH4kpaqwSTAQADAgADeQADNgQ",
        "Galya": "AgACAgIAAxkBAAIDZmlS2W63NbaEJt3WgGbQRimPIxhLAAJjDWsbwVKZSkUcFQRdAXGiAQADAgADeQADNgQ",
    },
}

ABOUT_PHOTOS = {
    1: None,
    2: None,
    3: None,
}


# ---------- KEYBOARDS ----------
def lang_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_ua")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇵🇹 Português", callback_data="lang_pt")],
        ]
    )


def save_user(user_id, full_name, username):
    cursor.execute(
        """
    INSERT OR IGNORE INTO users (user_id, full_name, username)
    VALUES (?, ?, ?)
    """,
        (user_id, full_name, username),
    )
    conn.commit()


def main_menu(lang):
    t = TEXTS[lang]["menu"]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["services"], callback_data="menu_services")],
            [InlineKeyboardButton(text=t["masters"], callback_data="menu_masters")],
            [InlineKeyboardButton(text=t["location"], callback_data="menu_location")],
            [InlineKeyboardButton(text=t["about"], callback_data="menu_about")],
        ]
    )


def back_book(lang, cat=None, from_masters=False):
    kb = [[InlineKeyboardButton(text=TEXTS[lang]["book"], url=MANAGER)]]

    if from_masters:
        kb.append(
            [
                InlineKeyboardButton(
                    text=TEXTS[lang]["back"], callback_data="menu_masters"
                )
            ]
        )
    elif cat:
        kb.append(
            [
                InlineKeyboardButton(
                    text=TEXTS[lang]["back"], callback_data=f"back_cat_{cat}"
                )
            ]
        )
    else:
        kb.append(
            [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_main")]
        )

    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_from_master(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["book"], url=MANAGER)],
            [
                InlineKeyboardButton(
                    text=TEXTS[lang]["back"], callback_data="menu_masters"
                )
            ],
        ]
    )


# ---------- START ----------
@dp.message(Command("start"))
async def start(msg: Message):
    save_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username)

    users_lang.pop(msg.from_user.id, None)
    await msg.answer(TEXTS["ua"]["lang"], reply_markup=lang_kb())


@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    users_lang[call.from_user.id] = lang
    await call.message.edit_text(TEXTS[lang]["welcome"], reply_markup=main_menu(lang))


# ---------- SERVICES ----------
@dp.callback_query(F.data == "menu_services")
async def services(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    kb = [
        [InlineKeyboardButton(text=c, callback_data=f"cat_{c}")] for c in SERVICES[lang]
    ]
    kb.append(
        [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_main")]
    )
    await call.message.edit_text(
        TEXTS[lang]["choose_category"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@dp.callback_query(F.data.startswith("cat_"))
async def category(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    cat = call.data[4:]
    kb = [
        [
            InlineKeyboardButton(
                text=v.split("\n")[0], callback_data=f"service_{cat}_{k}"
            )
        ]
        for k, v in SERVICES[lang][cat].items()
    ]
    kb.append(
        [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="menu_services")]
    )
    await call.message.edit_text(
        TEXTS[lang]["choose_service"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@dp.callback_query(F.data.startswith("service_"))
async def service(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    _, cat, key = call.data.split("_", 2)
    await call.message.edit_text(
        SERVICES[lang][cat][key], reply_markup=back_book(lang, cat)
    )


# ---------- MASTERS ----------


@dp.callback_query(F.data == "menu_masters")
async def masters(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")

    kb = [
        [InlineKeyboardButton(text=name, callback_data=f"master_{name}")]
        for name in MASTERS[lang]
    ]
    kb.append(
        [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_main")]
    )

    # Надсилаємо нове повідомлення без фото
    await call.message.answer(
        TEXTS[lang]["choose_master"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@dp.callback_query(F.data.startswith("master_"))
async def master(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    key = call.data.replace("master_", "")
    photo_id = MASTERS_PHOTOS[lang][key]

    # Відправляємо нове повідомлення з фото та описом
    await call.message.answer_photo(
        photo=photo_id, caption=MASTERS[lang][key], reply_markup=back_from_master(lang)
    )


# ---------- LOCATION / ABOUT ----------
@dp.callback_query(F.data == "menu_location")
async def location(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]["open_map"], url=MAP_URL)],
            [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_main")],
        ]
    )
    await call.message.edit_text(TEXTS[lang]["location_text"], reply_markup=kb)


@dp.callback_query(F.data == "menu_about")
async def about(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")

    media = []
    for i in sorted(ABOUT_PHOTOS.keys()):
        if ABOUT_PHOTOS[i]:
            caption = TEXTS[lang]["about_text"] if len(media) == 0 else None
            media.append(InputMediaPhoto(media=ABOUT_PHOTOS[i], caption=caption))

    if media:
        await call.message.answer_media_group(media)
    else:
        await call.message.answer(TEXTS[lang]["about_text"])


@dp.callback_query(F.data == "back_services")
async def back_services(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    kb = [
        [InlineKeyboardButton(text=c, callback_data=f"cat_{c}")] for c in SERVICES[lang]
    ]
    kb.append(
        [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_main")]
    )

    # await всередині async def — правильно
    await call.message.edit_text(
        TEXTS[lang]["choose_category"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@dp.callback_query(F.data.startswith("back_cat_"))
async def back_category(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    cat = call.data.replace("back_cat_", "")

    kb = [
        [
            InlineKeyboardButton(
                text=v.split("\n")[0], callback_data=f"service_{cat}_{k}"
            )
        ]
        for k, v in SERVICES[lang][cat].items()
    ]

    kb.append(
        [InlineKeyboardButton(text=TEXTS[lang]["back"], callback_data="back_services")]
    )

    await call.message.edit_text(
        TEXTS[lang]["choose_service"],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@dp.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery):
    lang = users_lang.get(call.from_user.id, "ua")
    await call.message.edit_text(TEXTS[lang]["welcome"], reply_markup=main_menu(lang))


# ---------- ADMIN ----------


@dp.message(Command("admin"))
async def admin(msg: Message):
    if msg.from_user.id not in ADMINS:  # перевірка на кількох адмінів
        return  # користувач не адмін, виходимо

    # Клавіатура адмін-панелі
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Розсилка", callback_data="broadcast")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
            [
                InlineKeyboardButton(
                    text="📸 Оновити фото майстра або салону",
                    callback_data="update_photo",
                )
            ],
        ]
    )

    await msg.answer("🔐 Адмін панель", reply_markup=kb)


@dp.callback_query(F.data == "update_photo")
async def start_photo_update(call: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📸 Фото майстра", callback_data="photo_master"
                )
            ],
            [InlineKeyboardButton(text="🏠 Фото салону", callback_data="photo_about")],
        ]
    )
    await call.message.answer("Оберіть, що хочете оновити:", reply_markup=kb)


# ---------- Хендлер для прийому фото ----------
@dp.message(PhotoUpdate.waiting, F.photo)
async def receive_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mode")

    file_id = msg.photo[-1].file_id
    caption = (msg.caption or "").strip()

    # --- ФОТО САЛОНУ ---
    if mode == "about":
        if not caption.isdigit():
            await msg.answer("❌ Вкажіть номер фото у підписі (1, 2, 3 …)")
            return

        ABOUT_PHOTOS[int(caption)] = file_id
        await msg.answer(f"✅ Фото салону №{caption} збережено")

    # --- ФОТО МАЙСТРА ---
    elif mode == "master":
        if not caption:
            await msg.answer("❌ Вкажіть імʼя майстра в підписі")
            return

        MASTERS_PHOTOS["ua"][caption] = file_id
        MASTERS_PHOTOS["ru"][caption] = file_id
        MASTERS_PHOTOS["pt"][caption] = file_id
        await msg.answer(f"✅ Фото майстра «{caption}» оновлено")

    else:
        await msg.answer("❌ Невідомий режим")

    await state.clear()


@dp.callback_query(F.data == "photo_about")
async def photo_about(call: CallbackQuery, state: FSMContext):
    await state.update_data(mode="about")
    await state.set_state(PhotoUpdate.waiting)
    await call.message.answer(
        "📸 Надішліть фото салону\n\nУ підписі вкажіть номер (1,2,3…)"
    )


@dp.callback_query(F.data == "photo_master")
async def photo_master(call: CallbackQuery, state: FSMContext):
    await state.update_data(mode="master")
    await state.set_state(PhotoUpdate.waiting)
    await call.message.answer(
        "📸 Надішліть фото майстра\n\nУ підписі вкажіть імʼя майстра"
    )


@dp.callback_query(F.data == "stats")
async def stats(call: CallbackQuery):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    await call.message.answer(f"👥 Користувачів: {count}")


@dp.callback_query(F.data == "broadcast")
async def broadcast_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(Broadcast.waiting)
    await call.message.answer("✏️ Надішліть текст або фото з текстом")


@dp.message(Broadcast.waiting)
async def broadcast_send(msg: Message, state: FSMContext):
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    sent = 0

    for (uid,) in users:
        try:
            if msg.photo:
                await bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption)
            else:
                await bot.send_message(uid, msg.text)
            sent += 1
        except:
            pass

    await msg.answer(f"✅ Відправлено: {sent}")
    await state.clear()


# ---------- RUN ----------
async def main():
    print("🔥 VERSION 2 LOADED")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
