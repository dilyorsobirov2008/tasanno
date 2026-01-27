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
ADMIN_ID = 7351189083 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ISH BO'LIMLARI TUGMALARI ---
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
        "⏳ **Tayyor bo'ling, so'rovnomani boshlaymiz...**"
    ),
    'ru': (
        "Здравствуйте 👋\n"
        "Этот бот предназначен для заполнения анкеты ✍️ и трудоустройства в Тасанно!\n"
        "⏳ **Будьте готовы, начинаем опрос...**"
    )
}

QUESTIONS = {
    'uz': [
        "👤 FISH kiriting:", "📆 Tug'ilgan sanangiz (03-04-1999):", "📍 Tug'ilgan joy va aniq manzil?", 
        "👨‍👩‍👧‍👦 Turmush qurganmisiz?", "💼 Qanday sohada o'qigansiz?", "📞 Telefon raqamingiz (+998...):", 
        "📞 Qo'shimcha telefon raqami:", # Yangi qo'shilgan savol
        "🧳 Ta'lim shakli?", "🎓 Ma'lumotingiz (Oliy yoki o'rta maxsus):", "🏫 Qaysi universitetda o'qigansiz yoki o'qiysiz?", 
        "🧑‍💻 Qanday dasturlarda ishlay olasiz?", "🇷🇺🇺🇿🇺🇸 Qaysi tillarni bilasiz?", "🔍📍 Tuman?", 
        "🧰 Qaysi sohalarda ishlamoqchisiz? (1 yoki 2 ta tanlang va 'Tasdiqlash'ni bosing):", 
        "💰 Oylik maoshni yozing (siz xohlagan):"
    ],
    'ru': [
        "👤 Введите ФИО:", "📆 Дата рождения (03-04-1999):", "📍 Место рождения и адрес?", 
        "👨‍👩‍👧‍👦 Семейное положение?", "💼 Сфера обучения?", "📞 Номер телефона (+998...):", 
        "📞 Дополнительный номер телефона:", # Yangi qo'shilgan savol
        "🧳 Форма обучения?", "🎓 Ваше образование:", "🏫 Университет?", 
        "🧑‍💻 В каких программах работаете?", "🇷🇺🇺🇿🇺🇸 Знание языков?", "🔍📍 Район?", 
        "🧰 В каких отделах хотите работать? (Выберите 1-2 и нажмите 'Подтвердить'):", 
        "💰 Желаемая зарплата:"
    ]
}

class Anketa(StatesGroup):
    lang = State()
    step = State()
    photo = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="l_uz")
    builder.button(text="🇷🇺 Русский", callback_data="l_ru")
    builder.adjust(1)
    await message.answer("Tilni tanlang / Выберите язык:", reply_markup=builder.as_markup())
    await state.set_state(Anketa.lang)

@dp.callback_query(F.data.startswith("l_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(chosen_lang=lang, answers=[], current_step=0, selected_jobs=[])
    await callback.message.answer(INFO_TEXTS[lang])
    await asyncio.sleep(2)
    await callback.message.answer(QUESTIONS[lang][0])
    await state.set_state(Anketa.step)
    await callback.answer()

# --- ISH TANLASH CALLBACK HANDLERI (2 TA TANLASH UCHUN) ---
@dp.callback_query(F.data.startswith("job_"))
async def job_selection(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get('selected_jobs', [])
    job = callback.data.replace("job_", "")
    lang = data['chosen_lang']

    if job in selected:
        selected.remove(job)
    elif len(selected) < 2:
        selected.append(job)
    else:
        return await callback.answer("Faqat 2 ta tanlash mumkin / Можно выбрать только 2", show_alert=True)

    await state.update_data(selected_jobs=selected)
    builder = InlineKeyboardBuilder()
    for j in JOBS[lang]:
        text = f"✅ {j}" if j in selected else j
        builder.button(text=text, callback_data=f"job_{j}")
    builder.button(text="✅ Tasdiqlash / Подтвердить", callback_data="confirm_jobs")
    builder.adjust(2)
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "confirm_jobs")
async def confirm_jobs(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get('selected_jobs', [])
    lang = data['chosen_lang']
    if not selected:
        return await callback.answer("Tanlang! / Выберите!", show_alert=True)
    
    answers = data['answers']
    answers.append(", ".join(selected))
    current_step = data['current_step'] + 1
    await state.update_data(answers=answers, current_step=current_step)
    await callback.message.answer(QUESTIONS[lang][current_step])
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
        if current_step == 13: # Savol qo'shilgani uchun index 12 dan 13 ga surildi
            builder = InlineKeyboardBuilder()
            for job in JOBS[lang]:
                builder.button(text=job, callback_data=f"job_{job}")
            builder.button(text="✅ Tasdiqlash / Подтвердить", callback_data="confirm_jobs")
            builder.adjust(2)
            await message.answer(QUESTIONS[lang][current_step], reply_markup=builder.as_markup())
        else:
            await message.answer(QUESTIONS[lang][current_step])
    else:
        await state.update_data(answers=answers)
        prompt = "Iltimos, rasmingizni yuboring (3x4 yoki selfi):" if lang == 'uz' else "Пожалуйста, отправьте ваше фото:"
        await message.answer(prompt)
        await state.set_state(Anketa.photo)

@dp.message(Anketa.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['chosen_lang']
    answers = data['answers']
    photo_id = message.photo[-1].file_id

    # Admin paneli uchun label'lar yangilandi
    labels = ["FISH", "Sana", "Manzil", "Oilaviy", "Soha", "Tel 1", "Tel 2", "Ta'lim", "Ma'lumot", "O'qish", "Dastur", "Til", "Tuman", "Ish", "Oylik"]
    report = f"🔔 **Yangi anketa ({lang})!**\n\n"
    for i, ans in enumerate(answers):
        if i < len(labels):
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
