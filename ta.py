import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web # Port uchun zarur kutubxona

# --- SOZLAMALAR ---
TOKEN = "8533561961:AAH327dM2cGjHC3-B5NovX_pKHzUwW_JdOg" 
ADMIN_ID = 7351189083 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- RENDER UCHUN PORT VA WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is running alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render avtomatik PORT o'zgaruvchisini beradi
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- MATNLAR LUG'ATI ---
INFO_TEXTS = {
    'uz': (
        "Salom 👋\n"
        "Ushbu bot Tasannoda anketalarni to'ldirish va mehnat uchun mo'ljallangan!\n"
        "Bu yerda siz o'zingizning arizangizni 📄 to'ldirishingiz ✍️ va "
        "bizning kompaniyamizdagi mavjud bo'sh ish o'rinlari haqida bilib olishingiz mumkin!\n\n"
        "Anketa savollari quyidagicha bo'ladi:\n"
        "👤: FISH\n"
        "📆: 03-04-1999\n"
        "📍: Tug'ilgan joy va aniq manzil?\n"
        "👨‍👩‍👧‍👦: Turmush qurganmisiz?\n"
        "💼: Qanday sohada o'qigansiz?\n"
        "📞: +998xxxxxxxxx telefon raqam?\n"
        "🧳: Ta'lim shakli?\n"
        "🎓: Ma'lumotingiz (Oliy yoki o'rta maxsus)\n"
        "🏫: Qaysi universitetda o'qigansiz yoki o'qiysiz\n"
        "🧑‍💻: Qanday dasturlarda ishlay olasiz?\n"
        "🇷🇺🇺🇿🇺🇸: Qaysi tillarni bilasiz?\n"
        "🔍📍: Tuman?\n"
        "🧰: Qanday ishda ishlashni xohlaysiz?\n"
        "💰: Oylik maoshni yozing (siz xohlagan)\n\n"
        "⏳ **Tayyor bo'ling, so'rovnomani boshlaymiz...**"
    ),
    'ru': (
        "Здравствуйте 👋\n"
        "Этот бот предназначен для заполнения анкеты ✍️ и трудоустройства в Тасанно!\n"
        "Здесь Вы можете заполнить свою анкету 📄 и узнать о вакансиях нашей Компании!\n\n"
        "Вопросы анкеты будут следующими:\n"
        "👤: ФИО\n"
        "📆: 03-04-1999\n"
        "📍: Место рождения и точный адрес?\n"
        "👨‍👩‍👧‍👦: Вы замужем/женаты?\n"
        "💼: В какой сфере Вы учились?\n"
        "📞: +998xxxxxxxxx номер телефона?\n"
        "🧳: Форма обучения?\n"
        "🎓: Ваше образование (Высшее или средне-специальное)\n"
        "🏫: В каком университете Вы учились или учитесь?\n"
        "🧑‍💻: В каких программах Вы умеете работать?\n"
        "🇷🇺🇺🇿🇺🇸: Какие языки Вы знаете?\n"
        "🔍📍: Район?\n"
        "🧰: На какой должности Вы хотите работать?\n"
        "💰: Напишите желаемую зарплату\n\n"
        "⏳ **Будьте готовы, начинаем опрос...**"
    )
}

QUESTIONS = {
    'uz': [
        "👤 FISH kiriting:", "📆 Tug'ilgan sanangiz (03-04-1999):", "📍 Tug'ilgan joy va aniq manzil?", 
        "👨‍👩‍👧‍👦 Turmush qurganmisiz?", "💼 Qanday sohada o'qigansiz?", "📞 Telefon raqamingiz (+998...):", 
        "🧳 Ta'lim shakli?", "🎓 Ma'lumotingiz (Oliy yoki o'rta maxsus):", "🏫 Qaysi universitetda o'qigansiz yoki o'qiysiz?", 
        "🧑‍💻 Qanday dasturlarda ishlay olasiz?", "🇷🇺🇺🇿🇺🇸 Qaysi tillarni bilasiz?", "🔍📍 Tuman?", 
        "🧰 Qanday ishda ishlashni xohlaysiz?", "💰 Oylik maoshni yozing (siz xohlagan):"
    ],
    'ru': [
        "👤 Введите ваше ФИО:", "📆 Введите дату рождения (03-04-1999):", "📍 Место рождения и ваш точный адрес?", 
        "👨‍👩‍👧‍👦 Вы замужем или женаты?", "💼 В какой сфере Вы учились?", "📞 Ваш номер телефона (+998...):", 
        "🧳 Ваша форма обучения?", "🎓 Ваше образование (Высшее или средне-специальное):", "🏫 В каком университете Вы учились или учитесь?", 
        "🧑‍💻 В каких программах Вы умеете работать?", "🇷🇺🇺🇿🇺🇸 Какие языки Вы знаете?", "🔍📍 Ваш район?", 
        "🧰 На какой должности Вы хотите работать?", "💰 Напишите желаемую зарплату:"
    ]
}

class Anketa(StatesGroup):
    lang = State()
    step = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="l_uz")
    builder.button(text="🇷🇺 Русский", callback_data="l_ru")
    builder.adjust(1)
    
    welcome = (
        "Tasanno savdo markazining ichki «Anketalar» to'ldirish botiga xush kelibsiz.\n"
        "Tilni tanlang / Выберите язык:"
    )
    await message.answer(welcome, reply_markup=builder.as_markup())
    await state.set_state(Anketa.lang)

@dp.callback_query(F.data.startswith("l_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(chosen_lang=lang, answers=[], current_step=0)
    
    await callback.message.answer(INFO_TEXTS[lang])
    
    await asyncio.sleep(3)
    await callback.message.answer(QUESTIONS[lang][0])
    await state.set_state(Anketa.step)
    await callback.answer()

@dp.message(Anketa.step)
async def process_steps(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['chosen_lang']
    current_step = data['current_step']
    answers = data['answers']
    
    answers.append(message.text)
    current_step += 1
    
    if current_step < len(QUESTIONS[lang]):
        await state.update_data(answers=answers, current_step=current_step)
        await message.answer(QUESTIONS[lang][current_step])
    else:
        labels = ["FISH", "Sana", "Manzil", "Oilaviy", "Soha", "Tel", "Ta'lim", "Ma'lumot", "O'qish joyi", "Dasturlar", "Tillari", "Tuman", "Ish", "Oylik"]
        report = f"🔔 **Yangi anketa ({lang})!**\n\n"
        for i, ans in enumerate(answers):
            report += f"🔹 **{labels[i]}:** {ans}\n"
        
        await bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
        
        thanks = "Rahmat! Ma'lumotlaringiz adminga yuborildi." if lang == 'uz' else "Спасибо! Ваши данные отправлены админу."
        await message.answer(thanks)
        await state.clear()

async def main():
    # Ham portni, ham botni baravar ishga tushirish
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass