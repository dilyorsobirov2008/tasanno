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
ADMIN_ID = 6339752659 # Admin botga /start bosgan bo'lishi shart!

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ISH BO'LIMLARI TUGMALARI ---
JOBS = {
    'uz': ["Ombor boʻlimi", "Sotuvchi", "Undiruvchi", "Shartnoma", "Kassa", "Operator", "Qorovul", "Arxivarius", "HR"],
    'ru': ["Складской отдел", "Продавец", "Взыскатель", "Контрактный отдел", "Кассир", "Оператор", "Охранник", "Архивариус", "HR"]
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
        "🏢: Oxirgi ishlagan joyingiz?\n"
        "🧰: Qanday ishda ishlashni xohlaysiz?\n"
        "💰: Oylik maoshni yozing (siz xohlagan)\n\n"
        "⏳ **Tayyor bo'ling, so'rovnomani boshlaymiz...**"
    ),
    'ru': (
        "Здравствуйте 👋\n"
        "Этот бот предназначен для заполнения анкеты ✍️ и трудоустройства в Тасанно!\n"
        "Здесь Вы можете заполнит свою анкету 📄 и узнать о вакансиях нашей Компании!\n\n"
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
        "🏢: Последнее место работы?\n"
        "🧰: На какой должности Вы хотите работать?\n"
        "💰: Напишите желаемую зарплату\n\n"
        "⏳ **Будьте готовы, начинаем опрос...**"
    )
}

QUESTIONS = {
    'uz': [
        "👤 FISH kiriting:", "📆 Tug'ilgan sanangiz (03-04-1999):", "📍 Tug'ilgan joy va aniq manzil?", 
        "👨‍👩‍👧‍👦 Turmush qurganmisiz?", "💼 Qanday sohada o'qigansiz?", "📞 Telefon raqamingiz (+998...):", 
        "📞 Qo'shimcha telefon raqami:", "🧳 Ta'lim shakli?", "🎓 Ma'lumotingiz (Oliy yoki o'rta maxsus):", 
        "🏫 Qaysi universitetda o'qigansiz yoki o'qiysiz?", "🧑‍💻 Qanday dasturlarda ishlay olasiz?", 
        "🇷🇺🇺🇿🇺🇸 Qaysi tillarni bilasiz?", "🔍📍 Tuman?", "🏢 Oxirgi ishlagan joyingiz:", 
        "🧰 Qaysi sohalarda ishlamoqchisiz? (1-2 ta tanlang va 'Tasdiqlash'ni bosing):", 
        "💰 Oylik maoshni yozing (siz xohlagan):"
    ],
    'ru': [
        "👤 Введите ваше ФИО:", "📆 Введите дату рождения (03-04-1999):", "📍 Место рождения и ваш точный адрес?", 
        "👨‍👩‍👧‍👦 Вы замужем или женаты?", "💼 В какой сфере Вы учились?", "📞 Ваш номер телефона (+998...):", 
        "📞 Дополнительный номер телефона:", "🧳 Ваша форма обучения?", "🎓 Ваше образование (Высшее или средне-специальное):", 
        "🏫 В каком университете Вы учились или учитесь?", "🧑‍💻 В каких программах Вы умеете работать?", 
        "🇷🇺🇺🇿🇺🇸 Какие языки Вы знаете?", "🔍📍 Ваш район?", "🏢 Последнее место работы:", 
        "🧰 В каких отделах хотите работать? (Выберите 1-2 и нажмите 'Подтвердить'):", 
        "💰 Напишите желаемую зарплату:"
    ]
}

class Anketa(StatesGroup):
    lang = State()
    branch = State()
    job_branch = State()
    step = State()
    photo = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    intro_text = (
        "🏢 TASANNO SAVDO MARKAZI\n\n"
        "“Tasanno” savdo markazi o‘z faoliyatini 2023-yil 15-iyun sanasida boshlagan bo‘lib, bugungi kunga qadar 60 dan ziyod fuqarolarni doimiy ish o‘rinlari bilan ta’minlab kelmoqda.\n\n"
        "Savdo markazining rivojlanishi natijasida filiallar tarmog‘i ham kengayib bormoqda. Jumladan, Marhamat filiali 2024-yil 2-mart sanasida ish faoliyatini boshlagan bo‘lib, hozirgi kunda 20 dan ortiq xodimlar faoliyat yuritmoqda.\n\n"
        "Shuningdek, Shahrixon filiali 2025-yil 25-may sanasida o‘z ishini boshlagan va qisqa vaqt ichida 20 dan ortiq xodimlarni ish bilan ta’minlashga erishgan.\n\n"
        "Bugungi kunda “Tasanno” savdo markazi mijozlarga barcha turdagi maishiy texnikalar, qurilish mollari, zamonaviy mebellar hamda sport mahsulotlarini keng assortimentda taklif etib kelmoqda. Sifatli mahsulotlar, qulay narxlar va mijozlar ehtiyojini birinchi o‘ringa qo‘ygan xizmat ko‘rsatish tamoyili savdo markazining asosiy ustuvor yo‘nalishlaridan hisoblanadi."
    )
    await message.answer(intro_text)
    
    await asyncio.sleep(3)

    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="l_uz")
    builder.button(text="🇷🇺 Русский", callback_data="l_ru")
    builder.adjust(1)
    await message.answer("Tasanno savdo markazining ichki «Anketalar» to'ldirish botiga xush kelibsiz.\nTilni tanlang / Выберите язык:", reply_markup=builder.as_markup())
    await state.set_state(Anketa.lang)

@dp.callback_query(F.data.startswith("l_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(chosen_lang=lang, answers=[], current_step=0, selected_jobs=[])
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏢 Shahrixon", callback_data="branch_shahrixon")
    builder.button(text="🏢 Marhamat", callback_data="branch_marhamat")
    builder.button(text="🏢 Asaka", callback_data="branch_asaka")
    builder.adjust(2)
    
    await callback.message.answer("📍 Filialni tanlang\n\nQaysi filial uchun anketa to'ldirmoqchisiz?", reply_markup=builder.as_markup())
    await state.set_state(Anketa.branch)
    await callback.answer()

@dp.callback_query(F.data.startswith("branch_"), Anketa.branch)
async def set_branch(callback: types.CallbackQuery, state: FSMContext):
    branch_map = {
        "branch_shahrixon": "Shahrixon",
        "branch_marhamat": "Marhamat",
        "branch_asaka": "Asaka"
    }
    selected_branch = branch_map.get(callback.data, "Noma'lum")
    await state.update_data(selected_branch=selected_branch)
    
    data = await state.get_data()
    lang = data['chosen_lang']
    
    if selected_branch in ["Shahrixon", "Marhamat"]:
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Reklama", callback_data="job_reklama")
        builder.button(text="📦 Ombor", callback_data="job_ombor")
        builder.button(text="💳 Shartnoma va kassa", callback_data="job_kassa")
        builder.button(text="💰 Undiruv", callback_data="job_undiruv")
        builder.button(text="👨💼 Sotuvchi-maslahatchi", callback_data="job_sotuvchi")
        builder.adjust(2, 2, 1)
        
        await callback.message.answer("💼 Ish yo'nalishini tanlang\n\nQuyidagi lavozimlardan birini tanlang:", reply_markup=builder.as_markup())
        await state.set_state(Anketa.job_branch)
        await callback.answer()
    else:
        await callback.message.answer(INFO_TEXTS[lang])
        await asyncio.sleep(1.5)
        await callback.message.answer(QUESTIONS[lang][0])
        await state.set_state(Anketa.step)
        await callback.answer()

@dp.callback_query(F.data.startswith("job_"), Anketa.job_branch)
async def set_job_branch(callback: types.CallbackQuery, state: FSMContext):
    job_map = {
        "job_reklama": "Reklama",
        "job_ombor": "Ombor",
        "job_kassa": "Shartnoma va kassa",
        "job_undiruv": "Undiruv",
        "job_sotuvchi": "Sotuvchi-maslahatchi"
    }
    selected_job = job_map.get(callback.data, "Noma'lum")
    await state.update_data(selected_job_branch=selected_job)
    
    data = await state.get_data()
    lang = data['chosen_lang']
    
    await callback.message.answer(INFO_TEXTS[lang])
    await asyncio.sleep(1.5)
    await callback.message.answer(QUESTIONS[lang][0])
    await state.set_state(Anketa.step)
    await callback.answer()

@dp.callback_query(F.data.startswith("job_"), Anketa.step)
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
        return await callback.answer("Faqat 2 ta tanlash mumkin!", show_alert=True)

    await state.update_data(selected_jobs=selected)
    builder = InlineKeyboardBuilder()
    for j in JOBS[lang]:
        text = f"✅ {j}" if j in selected else j
        builder.button(text=text, callback_data=f"job_{j}")
    builder.button(text="✅ Tasdiqlash / Подтвердить", callback_data="confirm_jobs")
    builder.adjust(2)
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "confirm_jobs", Anketa.step)
async def confirm_jobs(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get('selected_jobs', [])
    lang = data['chosen_lang']
    if not selected:
        return await callback.answer("Tanlang!", show_alert=True)
    
    answers = data.get('answers', [])
    answers.append(", ".join(selected))
    next_step = 15 # Keyingi savol - Maosh
    
    await state.update_data(answers=answers, current_step=next_step)
    await callback.message.answer(QUESTIONS[lang][next_step])
    await callback.answer()

@dp.message(Anketa.step)
async def process_steps(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['chosen_lang']
    current_step = data['current_step']
    answers = data.get('answers', [])
    
    if current_step == 14:
        return

    if message.text:
        answers.append(message.text)
    
    next_step = current_step + 1
    await state.update_data(answers=answers, current_step=next_step)
    
    if next_step < len(QUESTIONS[lang]):
        if next_step == 14: 
            builder = InlineKeyboardBuilder()
            for job in JOBS[lang]:
                builder.button(text=job, callback_data=f"job_{job}")
            builder.button(text="✅ Tasdiqlash / Подтвердить", callback_data="confirm_jobs")
            builder.adjust(2)
            await message.answer(QUESTIONS[lang][next_step], reply_markup=builder.as_markup())
        else:
            await message.answer(QUESTIONS[lang][next_step])
    else:
        prompt = "Iltimos, rasmingizni yuboring (3x4 yoki selfi):" if lang == 'uz' else "Пожалуйста, отправьте ваше фото (3х4 или селфи):"
        await message.answer(prompt)
        await state.set_state(Anketa.photo)

@dp.message(Anketa.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data['chosen_lang']
    answers = data['answers']
    photo_id = message.photo[-1].file_id

    labels = ["FISH", "Sana", "Manzil", "Oilaviy", "Soha", "Tel 1", "Tel 2", "Ta'lim", "Ma'lumot", "O'qish", "Dastur", "Til", "Tuman", "Oxirgi ish", "Ish", "Maosh"]
    selected_branch = data.get('selected_branch', 'Noma\'lum')
    selected_job_branch = data.get('selected_job_branch', '')
    
    report = f"🔔 Yangi anketa ({lang})!\n📍 Filial: {selected_branch}\n"
    if selected_job_branch:
        report += f"💼 Ish yo'nalishi: {selected_job_branch}\n"
    report += "\n"
    for i, ans in enumerate(answers):
        if i < len(labels):
            report += f"🔹 {labels[i]}: {ans}\n"
    
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=report)
        await message.answer("Rahmat! Ma'lumotlaringiz adminga yuborildi." if lang == 'uz' else "Спасибо! Ваши данные отправлены админу.")
        await state.clear()
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("Xatolik! Admin botni hali faollashtirmagan (Admin /start bosishi shart).")

async def main():
    asyncio.create_task(start_web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
