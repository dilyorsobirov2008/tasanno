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
ADMIN_IDS = [6339752659, 7351189083] # Adminlar botga /start bosgan bo'lishi shart!

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

SOTUVCHI_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzilingiz", "Telefon raqamingiz", 
    "Oilangiz haqida qisqacha ma'lumot", "Ma'lumotingiz (Oliy / O'rta maxsus / O'rta)", 
    "Qo'shimcha sertifikat yoki diplomlaringiz", "Oxirgi ish joyingiz (korxona nomi, lavozimi, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxsning F.I.Sh., lavozimi va telefon raqami", 
    "Maishiy texnika yoki nasiya savdo (kredit) sohasida qancha vaqt ishlagansiz?", 
    "Oldingi ish joyingizdagi eng katta shaxsiy sotuv ko'rsatkichingiz yoki yutug'ingiz nima?", 
    "Mijoz mahsulotni sotib olmoqchi, lekin hujjati yoki doimiy daromadi yo'q. Vaziyatdan qanday chiqasiz?", 
    "Oylik rejangizni bajarolmayotganingizni ko'rsangiz, oxirgi haftada nimalar qilasiz?", 
    "Konditsioner yoki xolodilnik sotayotganda mijozga uning afzalligini qanday tushuntirasiz? (Qisqa misol keltiring.)", 
    "Nima uchun aynan maishiy texnika va nasiya savdo sohasini tanladingiz?", 
    "Tasanno haqida qanday ma'lumotlarni bilasiz?", 
    "Do'konda qimmat telefonni sotish imkoni bor, lekin u mijozga to'g'ri kelmaydi. Siz qimmatini sotasizmi yoki foydalisini? Nega?", 
    "Bu ish orqali hayotingizdagi qaysi moliyaviy maqsadingizga (uy, mashina, qarzdan qutilish va hokazo) erishmoqchisiz?", 
    "Nasiya savdoga to'lov qilishga qiynalayotgan, asbobi buzilgan jahldor mijoz keldi. Unga qanday yordam berasiz?", 
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha (masalan, do'kon mudiri) ko'tarilmoqchisiz?", 
    "Do'kondagi hamkasbingiz kassadan pul olayotganini yoki qasddan xatoga yo'l qo'yayotganini ko'rib qoldingiz. Sizning harakatingiz qanday bo'ladi?", 
    "Mijoz juda injiq va qo'pol gapirmoqda. Unga xizmat ko'rsatishni davom ettirasizmi yoki boshqa sotuvchiga o'tkazasiz? Nega?", 
    "Bir vaqtning o'zida bir nechta mijoz sizga murojaat qilmoqda, ammo mahsulotni tasdiqlash uchun dasturga planshet orqali kira olmayapsiz. Bunday holatda qanday yo'l tutasiz?", 
    "Shaxsiy sotuv rejangizni bajarib bo'ldingiz, lekin jamoangiz reja ortida qolyapti. Ish vaqtingiz tugagach, uyga ketasizmi yoki jamoaga yordam berasiz? Nega?", 
    "Siz uchun bu ishda nima birinchi o'rinda: mijozning muammosini hal qilishmi yoki har bir sotuvdan keladigan shaxsiy bonus? Sababini yozing.", 
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingizni yozing."
]

REKLAMA_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "Reklama, marketing, SMM yoki dizayn sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish joyingizdagi eng muvaffaqiyatli reklama loyihangiz yoki yutug'ingiz haqida qisqacha ma'lumot bering.",
    "Qaysi dasturlar bilan ishlay olasiz? (Photoshop, CorelDRAW, Canva, Illustrator, CapCut, Premiere Pro va boshqalar)",
    "Ijtimoiy tarmoqlarda reklama berishda eng muhim omil nima deb hisoblaysiz?",
    "Tasanno savdo markazi haqida qanday ma'lumotlarni bilasiz?",
    "Savdo markazida chegirma aksiyasi boshlandi. Uni mijozlarga yetkazish uchun qanday reklama usullaridan foydalanardingiz?",
    "Instagram yoki Telegram uchun post tayyorlashda nimalarga e'tibor berasiz?",
    "Siz yaratgan reklama kutilgan natijani bermasa, qanday yo'l tutasiz?",
    "Bir vaqtning o'zida bir nechta filial uchun reklama materiali tayyorlash kerak bo'lsa, ishlarni qanday rejalashtirasiz?",
    "Mijozlar yoki rahbariyat tomonidan reklama dizayniga bir necha marta o'zgartirish kiritish so'ralganda qanday munosabat bildirasiz?",
    "Sizningcha, yaxshi reklama qanday bo'lishi kerak?",
    "Savdo markaziga xaridorlarni jalb qilish uchun qanday aksiya yoki marketing g'oyani taklif qilgan bo'lardingiz?",
    "Raqobatchilar reklamasini kuzatib borasizmi? Ulardan qanday xulosalar chiqarasiz?",
    "Reklama kampaniyasining muvaffaqiyatini qanday baholaysiz?",
    "Agar sizga juda qisqa muddatda banner, post va video tayyorlash topshirig'i berilsa, qanday yo'l tutasiz?",
    "Ijtimoiy tarmoqlardagi salbiy izohlar yoki tanqidlarga qanday munosabat bildirasiz?",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko'tarilishni maqsad qilgansiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Sizningcha, reklama bo'limi kompaniya rivojlanishiga qanday hissa qo'shadi?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingizni sanab bering.",
    "Instagram uchun post matni.",
    "Instagram/Facebook Story uchun qisqa matn.",
    "15 soniyalik reklama videosi uchun ssenariy."
]

OMBOR_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "Ombor, logistika yoki tovarlar bilan ishlash sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish joyingizdagi eng katta yutug'ingiz yoki natijangiz qanday bo'lgan?",
    "Ombor xodimi uchun eng muhim 3 ta sifat qaysilar deb hisoblaysiz?",
    "Tovar qabul qilish vaqtida hujjatdagi miqdor bilan amaldagi mahsulot soni mos kelmasa, qanday yo'l tutasiz?",
    "Omborda mahsulotlar tartibini qanday saqlaysiz?",
    "Bir vaqtning o'zida bir nechta mahsulot kirimi va chiqimi bo'lsa, ishlarni qanday tashkil qilasiz?",
    "Nima uchun aynan ombor bo'limi mutaxassisi lavozimida ishlashni xohlaysiz?",
    "Tasanno savdo markazi haqida qanday ma'lumotlarni bilasiz?",
    "Inventarizatsiya paytida kamomad aniqlansa, qanday harakat qilasiz?",
    "Qimmatbaho maishiy texnikalarni saqlashda nimalarga e'tibor berish kerak deb o'ylaysiz?",
    "Ombordagi mahsulotlardan biri shikastlanganini aniqlasangiz, nima qilasiz?",
    "Hamkasbingiz mahsulotlarni hisobga olmasdan olib chiqayotganini ko'rib qolsangiz, qanday yo'l tutasiz?",
    "Siz uchun ishda nima muhimroq: tezlikmi yoki aniqlik? Nima uchun?",
    "Bir vaqtning o'zida yuk mashinasi mahsulot olib keldi, mijozga mahsulot chiqarish kerak va rahbar hisobot so'radi. Vazifalarni qanday ustuvorlashtirasiz?",
    "Ombor dasturi ishlamay qolsa yoki mahsulotni tizimdan topa olmasangiz, qanday yo'l tutasiz?",
    "Jismoniy mehnat va mas'uliyat talab qiladigan ish sharoitiga qanday munosabatdasiz? (Sog'lig'ingiz bo'yicha ish faoliyatingizga ta'sir qiladigan muammolaringiz bormi?)",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko'tarilishni maqsad qilgansiz?",
    "Shaxsiy vazifalaringizni tugatdingiz, ammo hamkasblaringiz ishga ulgurmayapti. Nima qilasiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingizni sanab bering."
]

CALL_CENTER_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "Call-center, mijozlar bilan ishlash yoki savdo sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish joyingizdagi eng katta yutug'ingiz yoki natijangiz qanday bo'lgan?",
    "Nima uchun aynan Call Center operatori lavozimida ishlashni xohlaysiz?",
    "Telefon orqali muloqot qilishda sizningcha eng muhim 3 ta sifat qaysilar?",
    "Mijoz qo'ng'iroq davomida jahli chiqib, qo'pol gapirayotgan bo'lsa, qanday yo'l tutasiz?",
    "Mijozning muammosini darhol hal qila olmasangiz, unga qanday javob berasiz?",
    "Bir vaqtning o'zida qo'ng'iroqqa javob berish, ma'lumotlarni tizimga kiritish va yangi murojaatlarni qayd etish kerak bo'lsa, ishni qanday tashkil qilasiz?",
    "Tasanno savdo markazi haqida qanday ma'lumotlarni bilasiz?",
    "Mijoz siz so'ragan ma'lumotlarni berishni istamasa, suhbatni qanday davom ettirasiz?",
    "Kun davomida juda ko'p qo'ng'iroqlar bo'lsa, ish unumdorligingizni qanday saqlab qolasiz?",
    "Mijoz sizga bir xil savolni bir necha marta qayta bersa, qanday munosabat bildirasiz?",
    "Telefon orqali mahsulot yoki xizmat haqida qisqa va tushunarli ma'lumot bera olasizmi? Misol keltiring.",
    "Reja bo'yicha amalga oshirishingiz kerak bo'lgan qo'ng'iroqlar soniga yetmayotganingizni sezsangiz, nima qilasiz?",
    "Mijoz bilan gaplashayotganda tizim ishlamay qolsa yoki internet uzilib qolsa, vaziyatni qanday boshqarasiz?",
    "Hamkasbingiz mijoz bilan noto'g'ri muomala qilayotganini eshitsangiz, nima qilasiz?",
    "Siz uchun ishda nima muhimroq: qo'ng'iroqlar sonimi yoki mijozning muammosini sifatli hal qilishmi? Sababini tushuntiring.",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko'tarilishni maqsad qilgansiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Stressli vaziyatlarda o'zingizni qanday boshqarasiz?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingizni sanab bering."
]

KASSA_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "Kassa, shartnoma yoki mijozlarga xizmat ko‘rsatish sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish joyingizdagi eng katta yutug‘ingiz yoki natijangiz qanday bo‘lgan?",
    "Naqd pul bilan ishlashda siz uchun eng muhim qoida nima?",
    "Kassa yopilganda pul qoldig‘ida kamomad yoki ortiqcha summa aniqlansa, qanday yo‘l tutasiz?",
    "Mijoz shartnoma tuzishga kelgan, ammo hujjatlarida kamchilik mavjud. Bunday holatda nima qilasiz?",
    "Mijoz shartnoma shartlarini tushunmayotgan bo‘lsa, unga qanday tushuntirasiz?",
    "Bir vaqtning o‘zida kassada navbat paydo bo‘ldi va yangi shartnoma rasmiylashtirish kerak. Ishlarni qanday tashkil qilasiz?",
    "Nima uchun aynan shartnoma va kassa mutaxassisi lavozimida ishlashni xohlaysiz?",
    "Tasanno savdo markazi haqida qanday ma’lumotlarni bilasiz?",
    "Mijoz to‘lovni amalga oshirgandan so‘ng chek yoki hujjatda xatolik aniqlansa, qanday harakat qilasiz?",
    "Ish jarayonida sizga ishonib topshirilgan pul mablag‘lari va hujjatlarning xavfsizligini qanday ta’minlaysiz?",
    "Hamkasbingiz kassada qoidabuzarlik qilayotganini yoki hujjatlarni noto‘g‘ri rasmiylashtirayotganini ko‘rib qolsangiz, nima qilasiz?",
    "Siz uchun ishda nima muhimroq: tezkorlikmi yoki aniqlik? Nima uchun?",
    "Bir vaqtning o‘zida bir nechta mijoz sizga murojaat qilmoqda, dastur esa sekin ishlayapti. Bunday vaziyatda qanday yo‘l tutasiz?",
    "Mijoz norozilik bildirib, baland ovozda gapirmoqda. Vaziyatni qanday boshqarasiz?",
    "Kunning oxirida hisobot topshirish va kassani yopish jarayonini qanday amalga oshirasiz?",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko‘tarilishni maqsad qilgansiz?",
    "Shaxsiy vazifalaringizni bajarib bo‘lgansiz, ammo bo‘limingiz ish hajmi ko‘pligi sabab ortda qolmoqda. Nima qilasiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingizni sanab bering."
]

UNDIRUV_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "Undiruv, mijozlar bilan ishlash yoki savdo sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish faoliyatingizdagi eng katta yutug'ingiz yoki natijangiz qanday bo'lgan?",
    "Qarzdor mijoz telefon qo'ng'iroqlariga javob bermayapti. Bunday vaziyatda qanday yo'l tutasiz?",
    "Mijoz to'lovni amalga oshira olmasligini aytdi. Siz unga qanday yechim taklif qilasiz?",
    "Qarzdor mijoz siz bilan qo'pol muomalada bo'lsa, vaziyatni qanday boshqarasiz?",
    "Oylik undirish rejangiz ortda qolayotganini sezsangiz, natijani yaxshilash uchun qanday choralar ko'rasiz?",
    "Sizningcha, undiruv bo'limi mutaxassisi uchun eng muhim 3 ta sifat qaysilar?",
    "Nima uchun aynan undiruv bo'limi mutaxassisi lavozimida ishlashni xohlaysiz?",
    "Tasanno savdo markazi haqida qanday ma'lumotlarni bilasiz?",
    "Bir kunda 50 dan ortiq mijoz bilan bog'lanishingiz kerak bo'lsa, ish jarayonini qanday rejalashtirasiz?",
    "Mijoz qarzdorligini tan oladi, ammo to'lash muddatini doim kechiktiradi. Sizning harakatingiz qanday bo'ladi?",
    "Siz uchun ishda nima muhimroq: reja bajarilishi yoki mijoz bilan uzoq muddatli ijobiy munosabatni saqlab qolish? Sababini tushuntiring.",
    "Hamkasbingiz xizmat vazifasini bajarmayotgani yoki ma'lumotlarni yashirayotganini bilib qolsangiz, nima qilasiz?",
    "Bir vaqtning o'zida bir nechta mijozlar bilan bog'lanishingiz, hisobot topshirishingiz va rahbar topshirig'ini bajarishingiz kerak. Ishlarni qanday ustuvorlashtirasiz?",
    "Mijoz qarzdorligi bo'yicha siz aytgan va'dasini bajarmadi. Keyingi harakatingiz qanday bo'ladi?",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko'tarilishni maqsad qilgansiz?",
    "Shaxsiy rejangizni bajarib bo'lgansiz, ammo jamoangiz reja ortida qolmoqda. Bunday vaziyatda nima qilasiz?",
    "Stressli vaziyatlarda o'zingizni qanday boshqarasiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Sizni jamoamizga taklif qilishimiz uchun 3 ta eng kuchli jihatingizni sanab bering.",
    "Shaxsiy avtomobilingiz bormi? (Ha / Yo'q. Agar ha bo'lsa, rusumi va ishlab chiqarilgan yilini yozing.)"
]

HR_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "HR, kadrlar bo‘limi yoki xodimlar bilan ishlash sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish joyingizdagi eng katta yutug‘ingiz yoki natijangiz qanday bo‘lgan?",
    "HR mutaxassisi uchun eng muhim 3 ta sifat qaysilar deb hisoblaysiz?",
    "Bir oy ichida ko‘p sonli vakant lavozimlarni yopish vazifasi yuklatilsa, ishni qanday tashkil qilasiz?",
    "Nomzod suhbatda yaxshi taassurot qoldirdi, lekin tajribasi talabga mos emas. Qaroringiz qanday bo‘ladi?",
    "Xodimlar o‘rtasida kelishmovchilik yuzaga kelsa, vaziyatni qanday boshqarasiz?",
    "Nima uchun aynan HR sohasida ishlashni tanlagansiz?",
    "Tasanno savdo markazi haqida qanday ma’lumotlarni bilasiz?",
    "Yaxshi nomzodni suhbat davomida qanday aniqlaysiz?",
    "Sizningcha, xodimning ishga qabul qilinishida tajriba muhimmi yoki shaxsiy fazilatlari? Nima uchun?",
    "Xodim ishdan bo‘shash haqida ariza yozdi. Uni saqlab qolish uchun qanday harakat qilasiz?",
    "Bir vaqtning o‘zida suhbatlar tashkil qilish, hujjatlar tayyorlash va hisobot topshirish kerak bo‘lsa, ishlarni qanday rejalashtirasiz?",
    "Ishga qabul qilingan xodim sinov muddatida talab darajasida ishlamasa, qanday yo‘l tutasiz?",
    "Jamoada motivatsiya pasayganini sezsangiz, qanday choralar ko‘rasiz?",
    "HR mutaxassisi sifatida maxfiy ma’lumotlar bilan ishlashda nimalarga e'tibor berasiz?",
    "Rahbar sizdan qisqa muddat ichida yangi filial uchun xodimlar jamoasini shakllantirishni so‘radi. Qanday yo‘l tutasiz?",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko‘tarilishni maqsad qilgansiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Sizningcha, HR bo‘limining kompaniya rivojlanishidagi o‘rni qanday?",
    "Sizni jamoamizga taklif qilishimiz uchun 3 ta eng kuchli jihatingizni sanab bering.",
    "Sotuv menejeri lavozimi uchun qisqa va jozibador vakansiya matnini yozing.",
    "Nomzodni telefon orqali suhbatga taklif qilish uchun qanday gaplashishingizni yozing.",
    "Suhbat davomida nomzodga beradigan eng muhim 5 ta savolni yozing."
]

KASSIR_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)",
    "Kassir yoki mijozlarga xizmat ko‘rsatish sohasida qancha vaqt ishlagansiz?",
    "Oldingi ish joyingizdagi eng katta yutug‘ingiz yoki natijangiz qanday bo‘lgan?",
    "Kassir uchun eng muhim 3 ta sifat qaysilar deb hisoblaysiz?",
    "Kassa yopilganda pul qoldig‘ida kamomad aniqlansa, qanday yo‘l tutasiz?",
    "Mijoz mahsulot uchun to‘lov qilmoqchi, ammo bank kartasi orqali to‘lov o‘tmayapti. Bunday holatda nima qilasiz?",
    "Mijoz qaytim puli kam berilganini aytib norozilik bildirsa, vaziyatni qanday hal qilasiz?",
    "Nima uchun aynan kassir lavozimida ishlashni xohlaysiz?",
    "Bozorcha Supermarketi haqida qanday ma’lumotlarni bilasiz?",
    "Bir vaqtning o‘zida kassada uzun navbat hosil bo‘ldi. Mijozlarga xizmat ko‘rsatishni qanday tashkil qilasiz?",
    "Mijoz sizga qo‘pol muomala qilsa, qanday munosabat bildirasiz?",
    "Naqd pul va terminal orqali to‘lovlarni qabul qilishda nimalarga e'tibor berasiz?",
    "Kassa apparati yoki dastur ishlamay qolsa, qanday harakat qilasiz?",
    "Hamkasbingiz kassadan pul olayotganini yoki qoidabuzarlik qilayotganini ko‘rib qolsangiz, nima qilasiz?",
    "Ish davomida charchoq yoki stressni qanday boshqarasiz?",
    "Bir mijozning mahsulotlari hisoblanayotgan paytda boshqa mijoz sizdan yordam so‘radi. Qanday yo‘l tutasiz?",
    "Siz uchun ishda nima muhimroq: tezlikmi yoki aniqlik? Nima uchun?",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko‘tarilishni maqsad qilgansiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Ish jadvali bo‘yicha dam olish kunlari yoki kechki smenada ishlashga tayyormisiz?",
    "Sizni jamoamizga taklif qilishimiz uchun 3 ta eng kuchli jihatingizni sanab bering.",
    "Mijoz xaridi 487 500, to'lov 500 000. Qancha qaytim berasiz?",
    "Qaytim berishda nimalarga e'tibor berasiz?",
    "Navbat ko'p, tizim sekin bo'lganda o'zingizni qanday tutasiz?",
    "Mijozlarga vaziyatni qanday tushuntirasiz?",
    "Navbatni imkon qadar tez va sifatli boshqarish uchun qanday choralar ko'rasiz?"
]

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
        "🏢 *“TASANNO” SAVDO MARKAZI VA “BOZORCHA” SUPERMARKETI*\n\n"
        "“Tasanno” savdo markazi o‘z faoliyatini 2023-yil 15-iyun sanasida boshlagan bo‘lib, bugungi kunga qadar 100 dan ziyod fuqarolarni doimiy ish o‘rinlari bilan ta’minlab kelmoqda.\n\n"
        "Savdo markazining rivojlanishi natijasida filiallar tarmog‘i ham kengayib bormoqda. Jumladan, Marhamat filiali 2024-yil 2-mart sanasida ish faoliyatini boshlagan bo‘lib, hozirgi kunda 20 dan ortiq xodimlar faoliyat yuritmoqda.\n\n"
        "Shuningdek, Shahrixon filiali 2025-yil 25-may sanasida o‘z ishini boshlagan va qisqa vaqt ichida 20 dan ortiq xodimlarni ish bilan ta’minlashga erishgan.\n\n"
        "Kompaniya rivojlanishining navbatdagi bosqichi sifatida “Bozorcha” supermarketi 2025-yil 14-iyun sanasida o‘z faoliyatini boshladi. Bugungi kunda supermarketda 30 dan ziyod xodimlar faoliyat yuritib, aholini sifatli mahsulotlar va zamonaviy xizmat ko‘rsatish bilan ta’minlab kelmoqda.\n\n"
        "Bugungi kunda “Tasanno” savdo markazi mijozlarga barcha turdagi maishiy texnikalar, qurilish mollari, zamonaviy mebellar hamda sport mahsulotlarini keng assortimentda taklif etib kelmoqda. Shuningdek, “Bozorcha” supermarketi orqali kundalik ehtiyoj uchun zarur bo‘lgan oziq-ovqat va xalq iste’moli mahsulotlari aholiga taqdim etilmoqda.\n\n"
        "Sifatli mahsulotlar, qulay narxlar va mijozlar ehtiyojini birinchi o‘ringa qo‘ygan xizmat ko‘rsatish tamoyili kompaniyaning asosiy ustuvor yo‘nalishlaridan hisoblanadi.\n\n"
        "Bugungi kunda kompaniya tarkibidagi barcha filial va supermarketlarda jami 170 dan ortiq xodimlar faoliyat yuritib, aholi farovonligi va mijozlar ehtiyojlarini qondirish yo‘lida xizmat ko‘rsatib kelmoqda.\n\n"
        "“Tasanno” savdo markazi va “Bozorcha” supermarketi — ishonchli xaridlar, sifatli xizmat va barqaror rivojlanish manzili."
    )
    await message.answer(intro_text, parse_mode="Markdown")
    
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
    builder.button(text="🏢 Bozorcha", callback_data="branch_bozorcha")
    builder.adjust(2)
    
    await callback.message.answer("📍 Filialni tanlang\n\nQaysi filial uchun anketa to'ldirmoqchisiz?", reply_markup=builder.as_markup())
    await state.set_state(Anketa.branch)
    await callback.answer()

@dp.callback_query(F.data.startswith("branch_"), Anketa.branch)
async def set_branch(callback: types.CallbackQuery, state: FSMContext):
    branch_map = {
        "branch_shahrixon": "Shahrixon",
        "branch_marhamat": "Marhamat",
        "branch_asaka": "Asaka",
        "branch_bozorcha": "Bozorcha"
    }
    selected_branch = branch_map.get(callback.data, "Noma'lum")
    await state.update_data(selected_branch=selected_branch)
    
    builder = InlineKeyboardBuilder()
    if selected_branch == "Bozorcha":
        builder.button(text="💵 Kassir", callback_data="job_kassir")
        builder.adjust(1)
    else:
        builder.button(text="📢 Reklama", callback_data="job_reklama")
        builder.button(text="📦 Ombor", callback_data="job_ombor")
        builder.button(text="💳 Shartnoma va kassa", callback_data="job_kassa")
        builder.button(text="💰 Undiruv", callback_data="job_undiruv")
        builder.button(text="👨💼 Sotuvchi-maslahatchi", callback_data="job_sotuvchi")
        
        if selected_branch == "Asaka":
            builder.button(text="👨💼 HR", callback_data="job_hr")
            builder.button(text="🎧 Call Center", callback_data="job_call_center")
            builder.adjust(2, 2, 2, 1)
        else:
            builder.adjust(2, 2, 1)
    
    await callback.message.answer("💼 Ish yo'nalishini tanlang\n\nQuyidagi lavozimlardan birini tanlang:", reply_markup=builder.as_markup())
    await state.set_state(Anketa.job_branch)
    await callback.answer()

@dp.callback_query(F.data.startswith("job_"), Anketa.job_branch)
async def set_job_branch(callback: types.CallbackQuery, state: FSMContext):
    job_map = {
        "job_reklama": "Reklama",
        "job_ombor": "Ombor",
        "job_kassa": "Shartnoma va kassa",
        "job_undiruv": "Undiruv",
        "job_sotuvchi": "Sotuvchi-maslahatchi",
        "job_hr": "HR",
        "job_call_center": "Call Center",
        "job_kassir": "Kassir"
    }
    selected_job = job_map.get(callback.data, "Noma'lum")
    is_sotuvchi = selected_job == "Sotuvchi-maslahatchi"
    is_reklama = selected_job == "Reklama"
    is_ombor = selected_job == "Ombor"
    is_call_center = selected_job == "Call Center"
    is_kassa = selected_job == "Shartnoma va kassa"
    is_undiruv = selected_job == "Undiruv"
    is_hr = selected_job == "HR"
    is_kassir = selected_job == "Kassir"
    await state.update_data(selected_job_branch=selected_job, is_sotuvchi=is_sotuvchi, is_reklama=is_reklama, is_ombor=is_ombor, is_call_center=is_call_center, is_kassa=is_kassa, is_undiruv=is_undiruv, is_hr=is_hr, is_kassir=is_kassir)
    
    data = await state.get_data()
    lang = data['chosen_lang']
    
    await callback.message.answer(INFO_TEXTS[lang])
    await asyncio.sleep(1.5)
    
    if is_sotuvchi:
        q_list = SOTUVCHI_QUESTIONS
    elif is_reklama:
        q_list = REKLAMA_QUESTIONS
    elif is_ombor:
        q_list = OMBOR_QUESTIONS
    elif is_call_center:
        q_list = CALL_CENTER_QUESTIONS
    elif is_kassa:
        q_list = KASSA_QUESTIONS
    elif is_undiruv:
        q_list = UNDIRUV_QUESTIONS
    else:
        q_list = QUESTIONS[lang]
        
    await callback.message.answer(q_list[0])
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
    is_sotuvchi = data.get('is_sotuvchi', False)
    is_reklama = data.get('is_reklama', False)
    is_ombor = data.get('is_ombor', False)
    is_call_center = data.get('is_call_center', False)
    is_kassa = data.get('is_kassa', False)
    is_undiruv = data.get('is_undiruv', False)
    is_hr = data.get('is_hr', False)
    is_kassir = data.get('is_kassir', False)
    
    if is_sotuvchi:
        q_list = SOTUVCHI_QUESTIONS
    elif is_reklama:
        q_list = REKLAMA_QUESTIONS
    elif is_ombor:
        q_list = OMBOR_QUESTIONS
    elif is_call_center:
        q_list = CALL_CENTER_QUESTIONS
    elif is_kassa:
        q_list = KASSA_QUESTIONS
    elif is_undiruv:
        q_list = UNDIRUV_QUESTIONS
    elif is_hr:
        q_list = HR_QUESTIONS
    elif is_kassir:
        q_list = KASSIR_QUESTIONS
    else:
        q_list = QUESTIONS[lang]
    
    if not (is_sotuvchi or is_reklama or is_ombor or is_call_center or is_kassa or is_undiruv or is_hr) and current_step == 14:
        return

    if message.text:
        answers.append(message.text)
    
    next_step = current_step + 1
    await state.update_data(answers=answers, current_step=next_step)
    
    if next_step < len(q_list):
        if not (is_sotuvchi or is_reklama or is_ombor or is_call_center or is_kassa or is_undiruv or is_hr or is_kassir) and next_step == 14: 
            builder = InlineKeyboardBuilder()
            for job in JOBS[lang]:
                builder.button(text=job, callback_data=f"job_{job}")
            builder.button(text="✅ Tasdiqlash / Подтвердить", callback_data="confirm_jobs")
            builder.adjust(2)
            await message.answer(q_list[next_step], reply_markup=builder.as_markup())
        else:
            await message.answer(q_list[next_step])
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
    is_sotuvchi = data.get('is_sotuvchi', False)
    is_reklama = data.get('is_reklama', False)
    is_ombor = data.get('is_ombor', False)
    is_call_center = data.get('is_call_center', False)
    is_kassa = data.get('is_kassa', False)
    is_undiruv = data.get('is_undiruv', False)
    is_hr = data.get('is_hr', False)
    is_kassir = data.get('is_kassir', False)
    if is_sotuvchi:
        labels = SOTUVCHI_QUESTIONS
    elif is_reklama:
        labels = REKLAMA_QUESTIONS
    elif is_ombor:
        labels = OMBOR_QUESTIONS
    elif is_call_center:
        labels = CALL_CENTER_QUESTIONS
    elif is_kassa:
        labels = KASSA_QUESTIONS
    elif is_undiruv:
        labels = UNDIRUV_QUESTIONS
    elif is_hr:
        labels = HR_QUESTIONS
    elif is_kassir:
        labels = KASSIR_QUESTIONS

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
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_photo(chat_id=admin_id, photo=photo_id, caption=report)
            except Exception as e:
                logging.error(f"Admin {admin_id} ga yuborishda xatolik: {e}")
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
