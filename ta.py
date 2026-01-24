import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- SOZLAMALAR ---
TOKEN = "8533561961:AAH327dM2cGjHC3-B5NovX_pKHzUwW_JdOg" 
ADMIN_ID = 6339752659 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ISH BO'LIMLARI TUGMALARI (Tilingizga moslangan) ---
JOBS = {
    'uz': ["Ombor boʻlimi", "Sotuvchi", "Undiruvchi", "Shartnoma", "Kassa", "Operator", "Qorovul"],
    'ru': ["Складской отдел", "Продавец", "Взыскатель", "Контрактный отдел", "Кассир", "Оператор", "Охранник"]
}

# --- RENDER UCHUN PORT VA WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is running alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
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
        "bizning kompanimizdagi mavjud bo'sh ish o'rinlari haqida bilib olishingiz mumkin!\n\n"
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
        "🧰 Qanday ishda ishlashni xohlaysiz? (Quyidagilardan birini tanlang):", "💰 Oylik maoshni yozing (siz xohlagan):"
    ],
    'ru': [
        "👤 Введите ваше ФИО:", "📆 Введите дату рождения (03-04-1999):", "📍 Место рождения и ваш точный адрес?", 
        "👨‍👩‍👧‍👦 Вы замужем или женаты?", "💼 В какой сфере Вы учились?", "📞 Ваш номер телефона (+998...):", 
        "🧳 Ваша форма обучения?", "🎓 Ваше образование (Высшее или средне-специальное):", "🏫 В каком университете Вы учились или учитесь?", 
        "🧑‍💻 В каких программах Вы умеете работать?", "🇷🇺🇺🇿🇺🇸 Какие языки Вы знаете?", "🔍📍 Ваш район?", 
        "🧰 На какой должности Вы хотите работать? (Выберите из списка):", "💰 Напишите желаемую зарплату:"
    ]
}

class Anketa(StatesGroup):
    lang = State()
    step = State()
    photo = State() # Rasm uchun holat

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
@dp.callback_query(Anketa.step)
async def process_steps(event: types.Message | types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data['chosen_lang']
    current_step = data['current_step']
    answers = data['answers']
    
    if isinstance(event, types.CallbackQuery):
        answer = event.data.replace("job_", "")
        await event.answer()
    else:
        answer = event.text

    answers.append(answer)
    current_step += 1
    
    if current_step < len(QUESTIONS[lang]):
        await state.update_data(answers=answers, current_step=current_step)
        if current_step == 12:
            builder = InlineKeyboardBuilder()
            for job in JOBS[lang]: # Tilga mos ish o'rinlari
                builder.button(text=job, callback_data=f"job_{job}")
            builder.adjust(2)
            msg_obj = event.message if isinstance(event, types.CallbackQuery) else event
            await msg_obj.answer(QUESTIONS[lang][current_step], reply_markup=builder.as_markup())
        else:
            msg_obj = event.message if isinstance(event, types.CallbackQuery) else event
            await msg_obj.answer(QUESTIONS[lang][current_step])
    else:
        # Oxirgi savoldan keyin rasm so'rash
        await state.update_data(answers=answers)
        msg_obj = event.message if isinstance(event, types.CallbackQuery) else event
        prompt = "Iltimos, rasmingizni yuboring (3x4 yoki selfi):" if lang == 'uz' else "Пожалуйста, отправьте ваше фото:"
        await msg_obj.answer(prompt)
        await state.set_state(Anketa.photo)

@dp.message(Anketa.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['chosen_lang']
    answers = data['answers']
    photo_id = message.photo[-1].file_id

    labels = ["FISH", "Sana", "Manzil", "Oilaviy", "Soha", "Tel", "Ta'lim", "Ma'lumot", "O'qish joyi", "Dasturlar", "Tillari", "Tuman", "Ish", "Oylik"]
    report = f"🔔 **Yangi anketa ({lang})!**\n\n"
    for i, ans in enumerate(answers):
        report += f"🔹 **{labels[i]}:** {ans}\n"
    
    await bot.send_photo(ADMIN_ID, photo_id, caption=report, parse_mode="Markdown")
    
    thanks = "Rahmat! Ma'lumotlaringiz va rasm adminga yuborildi." if lang == 'uz' else "Спасибо! Ваши данные и фото отправлены админу."
    await message.answer(thanks)
    await state.clear()

async def main():
    await asyncio.gather(start_web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
