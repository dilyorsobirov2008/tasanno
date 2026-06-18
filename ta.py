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
TOKEN = "8946866791:AAHZh-85Ud1oJbrbmGAb4mR6Wey2gjSIu48" 
ADMIN_IDS = [6339752659, 7351189083]

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
        "bizning kompaniyimizdagi mavjud bo'sh ish o'rinlari haqida bilib olishingiz mumkin!\n\n"
        "⏳ **Tayyor bo'ling, so'rovnoma boshlanadi...**"
    ),
    'ru': (
        "Здравствуйте 👋\n"
        "Этот бот предназначен для заполнения анкеты ✍️ и трудоустройства в Тасанно!\n"
        "Здесь Вы можете заполнить свою анкеты 📄 и узнать о вакансиях нашей Компании!\n\n"
        "⏳ **Будьте готовы, опрос начинается...**"
    )
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
    "Bir vaqtning o'zida bir nechta mijoz sizga murojaat qilmoqda, ammo mahsulotni tasdiqlash uchun darsrturga planshet orqali kira olmayapsiz. Bunday holatda qanday yo'l tutasiz?", 
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
    "Hamkasbingiz xizmat vazifasini bajarmayotgani yoki ma'lumotlarni yashirayotgani bilib qolsangiz, nima qilasiz?",
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
    "Bir mijoz mahsulotlari hisoblanayotgan paytda boshqa mijoz sizdan yordam so‘radi. Qanday yo‘l tutasiz?",
    "Siz uchun ishda nima muhimroq: tezlikmi yoki aniqlik? Nima uchun?",
    "Kompaniyamizda qancha vaqt ishlab, qaysi lavozimgacha ko‘tarilishni maqsad qilgansiz?",
    "Ushbu ish orqali hayotingizdagi qaysi moliyaviy maqsadlaringizga erishmoqchisiz?",
    "Ish jadvali bo‘yicha dam olish kunlari yoki kechki smenada ishlashga tayyormisiz?",
    "Sizni jamoamizga taklif qilishimiz uchun 3 ta eng kuchli jihatingizni sanab bering.",
    "Mijoz xaridi 487 500, to'lov 500 000. Qancha qaytim berasiz?",
    "Qaytim berishda nimalarga e'tibor berasiz?",
    "Navbat ko'p, tizim sekin bo'lganda o'zingizni qanday tutasiz?",
    "Mijozlarga vaziyatni qanday tushuntirasiz?",
    "Navbatni imkon qadar tez va sifatli boshqarish uchun qanday choralar ko'raxasiz?"
]

BOZORCHA_COMMON_QUESTIONS = [
    "F.I.Sh.", "Tug‘ilgan sana (kun/oy/yil)", "Yashash manzili", "Telefon raqami", 
    "Oilaviy holati", "Ma’lumoti (oliy, o‘rta maxsus, o‘rta)", 
    "Qo‘shimcha sertifikat va diplomlari", "Oxirgi ish joyingiz (korxona nomi, lavozim, ketish sababi)", 
    "Avvalgi ish joyingizdan tavsiyanoma bera oladigan shaxs (F.I.Sh., lavozimi, telefon raqami)"
]

BOZORCHA_OMBOR_QUESTIONS = BOZORCHA_COMMON_QUESTIONS + [
    "Ombor sohasida qancha vaqt ishlagansiz?",
    "Eng katta yutug'ingiz qanday bo'lgan?",
    "Ombor xodimi uchun muhim 3 ta sifat?",
    "Tovar miqdori mos kelmasa nima qilasiz?",
    "Omborda mahsulotlar tartibini qanday saqlaysiz?",
    "Nima uchun aynan ombor bo'limini tanladingiz?",
    "Bozorcha haqida nimalarni bilasiz?",
    "Inventarizatsiya paytida kamomad aniqlansa nima qilasiz?",
    "Mahsulot shikastlanganini aniqlasangiz nima qilasiz?",
    "Siz uchun ishda nima muhimroq: tezlikmi yoki aniqlik?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingiz?"
]

BOZORCHA_SOTUVCHI_QUESTIONS = BOZORCHA_COMMON_QUESTIONS + [
    "Sotuv sohasida qancha vaqt ishlagansiz?",
    "Eng katta yutug'ingiz qanday bo'lgan?",
    "Sotuvchi uchun muhim 3 ta sifat?",
    "Mijoz e'tiroz bildirganda nima qilasiz?",
    "Mijozga biror narsani afzalligini qanday tushuntirasiz?",
    "Nima uchun aynan sotuvchi bo'limini tanladingiz?",
    "Bozorcha haqida nimalarni bilasiz?",
    "Sotuv rejasini qanday bajarasiz?",
    "Qimmat mahsulotni sotish siri nimada?",
    "Siz uchun ishda nima muhimroq: mijozmi yoki sotuv?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingiz?"
]

BOZORCHA_QOROVUL_QUESTIONS = BOZORCHA_COMMON_QUESTIONS + [
    "Qo'riqlash yoki xavfsizlik sohasida qancha vaqt ishlagansiz?",
    "Qo'riqlovchi uchun muhim 3 ta sifat?",
    "Shubhali shaxsni ko'rib qolsangiz nima qilasiz?",
    "O'g'rilik sodir bo'lganda birinchi harakatingiz?",
    "Kechki smenada ishlashga tayyormisiz?",
    "Jismoniy tayyorgarligingiz qanday?",
    "Bozorcha haqida nimalarni bilasiz?",
    "Xavfsizlik tizimlari (kamera, signalizatsiya) bilan ishlaganmisiz?",
    "Ziddiyatli vaziyatlarda (mijoz bilan tortishuv) o'zingizni qanday tutasiz?",
    "Nima uchun aynan qo'riqlash xizmatini tanladingiz?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingiz?"
]

BOZORCHA_KASSIR_QUESTIONS = BOZORCHA_COMMON_QUESTIONS + [
    "Kassir yoki mijozlarga xizmat ko‘rsatish sohasida qancha vaqt ishlagansiz?",
    "Kassir uchun eng muhim 3 ta sifat?",
    "Kassa yopilganda kamomad aniqlansa nima qilasiz?",
    "Bank kartasi orqali to‘lov o‘tmay qolsa nima qilasiz?",
    "Qaytim puli haqida e'tiroz bo'lsa vaziyatni qanday hal qilasiz?",
    "Bozorcha Supermarketi haqida nimalarni bilasiz?",
    "Navbatlar ko'payib ketganda ishingizni qanday tashkil qilasiz?",
    "Terminal va naqd pul bilan ishlashda nimalarga e'tibor berasiz?",
    "Kassa dasturi ishlamay qolsa nima qilasiz?",
    "Siz uchun ishda nima muhimroq: tezlikmi yoki aniqlik?",
    "Sizni jamoamizga taklif qilishimiz uchun eng kuchli 3 ta jihatingiz?"
]

# --- YO‘NALISH BO‘YICHA SAVOLLAR ---
QUESTIONS_BY_BRANCH = {
    "tasanno": {
        "sotuvchi": SOTUVCHI_QUESTIONS,
        "ombor": OMBOR_QUESTIONS,
        "call_center": CALL_CENTER_QUESTIONS,
        "kassa": KASSA_QUESTIONS,
        "undiruv": UNDIRUV_QUESTIONS,
        "hr": HR_QUESTIONS,
        "reklama": REKLAMA_QUESTIONS,
        "kassir": KASSIR_QUESTIONS,
    },
    "bozorcha": {
        "ombor": BOZORCHA_OMBOR_QUESTIONS,
        "sotuvchi": BOZORCHA_SOTUVCHI_QUESTIONS,
        "qorovul": BOZORCHA_QOROVUL_QUESTIONS,
        "kassir": BOZORCHA_KASSIR_QUESTIONS,
    }
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
    await asyncio.sleep(2)

    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbekcha", callback_data="l_uz")
    builder.button(text="🇷🇺 Русский", callback_data="l_ru")
    builder.adjust(1)
    await message.answer("Tasanno savdo markazining ichki «Anketalar» to'ldirish botiga xush kelibsiz.\nTilni tanlang / Выберите язык:", reply_markup=builder.as_markup())
    await state.set_state(Anketa.lang)

@dp.callback_query(F.data.startswith("l_"))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(chosen_lang=lang, answers=[], current_step=0)
    
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
        "branch_bozorcha": "Bozorcha Supermarketi"
    }
    
    selected_branch_id = callback.data
    selected_branch_name = branch_map.get(selected_branch_id, "Noma'lum")
    
    # Filial guruhini aniqlash (Bozorcha yoki Tasanno)
    branch_group = "bozorcha" if selected_branch_id == "branch_bozorcha" else "tasanno"
    
    await state.update_data(
        selected_branch=selected_branch_name,
        branch_group=branch_group
    )
    
    builder = InlineKeyboardBuilder()
    if branch_group == "bozorcha":
        builder.button(text="📦 Ombor bo'limi", callback_data="job_ombor")
        builder.button(text="👨💼 Sotuvchi", callback_data="job_sotuvchi")
        builder.button(text="🛡 Qo'riqlash xizmati", callback_data="job_qorovul")
        builder.button(text="💵 Kassir", callback_data="job_kassir")
        builder.adjust(2)
    else:
        builder.button(text="📢 Reklama", callback_data="job_reklama")
        builder.button(text="📦 Ombor", callback_data="job_ombor")
        builder.button(text="💳 Shartnoma va kassa", callback_data="job_kassa")
        builder.button(text="💰 Undiruv", callback_data="job_undiruv")
        builder.button(text="👨💼 Sotuvchi-maslahatchi", callback_data="job_sotuvchi")
        
        if selected_branch_name == "Asaka":
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
        "job_reklama": "reklama",
        "job_ombor": "ombor",
        "job_kassa": "kassa",
        "job_undiruv": "undiruv",
        "job_sotuvchi": "sotuvchi",
        "job_hr": "hr",
        "job_call_center": "call_center",
        "job_kassir": "kassir",
        "job_qorovul": "qorovul"
    }
    selected_role = job_map.get(callback.data, "noma'lum")
    
    role_names = {
        "reklama": "Reklama bo'limi",
        "ombor": "Ombor bo'limi",
        "kassa": "Kassa",
        "undiruv": "Undiruv",
        "sotuvchi": "Sotuvchi",
        "hr": "HR",
        "call_center": "Call-center",
        "kassir": "Kassir",
        "qorovul": "Qo'riqlash xizmati (Oxrana)"
    }
    
    data = await state.get_data()
    branch_group = data.get('branch_group', 'tasanno')
    
    await state.update_data(
        selected_role=selected_role, 
        selected_job_name=role_names.get(selected_role, "Noma'lum")
    )
    
    lang = data['chosen_lang']
    
    await callback.message.answer(INFO_TEXTS[lang], parse_mode="Markdown")
    await asyncio.sleep(1.5)
    
    # Savollarni filiallarga qarab olish
    branch_questions = QUESTIONS_BY_BRANCH.get(branch_group, {})
    q_list = branch_questions.get(selected_role, [])
    
    if not q_list:
        return await callback.answer("Savollar topilmadi.", show_alert=True)
        
    await callback.message.answer(q_list[0])
    await state.set_state(Anketa.step)
    await callback.answer()

@dp.message(Anketa.step)
async def process_steps(message: types.Message, state: FSMContext):
    if not message.text:
        return await message.answer("Iltimos, javobni matn shaklida yuboring.")

    data = await state.get_data()
    lang = data['chosen_lang']
    current_step = data['current_step']
    answers = data.get('answers', [])
    selected_role = data.get('selected_role')
    branch_group = data.get('branch_group', 'tasanno')
    
    branch_questions = QUESTIONS_BY_BRANCH.get(branch_group, {})
    q_list = branch_questions.get(selected_role, [])
    
    if not q_list:
        return

    answers.append(message.text)
    next_step = current_step + 1
    await state.update_data(answers=answers, current_step=next_step)
    
    if next_step < len(q_list):
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
    selected_branch = data.get('selected_branch', 'Noma\'lum')
    selected_role = data.get('selected_role')
    selected_job_name = data.get('selected_job_name', 'Noma\'lum')
    branch_group = data.get('branch_group', 'tasanno')
    
    branch_questions = QUESTIONS_BY_BRANCH.get(branch_group, {})
    labels = branch_questions.get(selected_role, [])

    # Hisobot matnini tayyorlash
    report = f"🔔 <b>YANGI ANKETA ({lang.upper()})!</b>\n\n"
    report += f"🏢 <b>Filial:</b> {selected_branch}\n"
    report += f"💼 <b>Lavozim:</b> {selected_job_name}\n"
    report += "----------------------------------\n"
    
    for i, ans in enumerate(answers):
        label = labels[i] if i < len(labels) else f"Savol {i+1}"
        report += f"🔹 <b>{label}:</b> {ans}\n"

    # Adminlar uchun tugmalar yaratish
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ijobiy", callback_data=f"ans_ijobiy_{message.from_user.id}")
    builder.button(text="🟡 Zaxira", callback_data=f"ans_zaxira_{message.from_user.id}")
    builder.button(text="❌ Rad etish", callback_data=f"ans_rad_{message.from_user.id}")
    builder.adjust(3)
    keyboard = builder.as_markup()

    success_notified = False
    broadcast_data = [] # Barcha adminlardagi xabar ID larini saqlash uchun
    
    for admin_id in ADMIN_IDS:
        try:
            # Hisobot va rasmni barcha adminlarga yuborish
            # Tugmalar faqat matnli xabarga qo'shiladi
            admin_msg = await bot.send_message(chat_id=admin_id, text=report, parse_mode="HTML", reply_markup=keyboard)
            await bot.send_photo(chat_id=admin_id, photo=photo_id, caption=f"Anketa egasining rasmi: {answers[0] if answers else ''}")
            broadcast_data.append((admin_id, admin_msg.message_id))
            success_notified = True
        except Exception as e:
            logging.error(f"Admin {admin_id} ga anketa yuborishda xatolik: {e}")

    if success_notified:
        # Xabar ID larini saqlash (qayta ishlash uchun)
        if not hasattr(bot, 'anketa_tracking'):
            bot.anketa_tracking = {}
        bot.anketa_tracking[str(message.from_user.id)] = broadcast_data

        confirmation_text = (
            "Hurmatli nomzod!\n\n"
            "Anketangiz muvaffaqiyatli qabul qilindi. Ma'lumotlaringiz ko'rib chiqilgach, "
            "3 ish kuni ichida siz bilan bog'lanamiz va natija haqida xabar beramiz.\n\n"
            "E'tiboringiz uchun rahmat va sizga omad tilaymiz!\n\n"
            "Tasanno Savdo Markazi & Bozorcha Supermarketi\n"
            "HR bo'limi"
        )
        await message.answer(confirmation_text)
        await state.clear()
    else:
        error_msg = "Xatolik yuz berdi. Anketani yuborishda muammo bo'ldi. Iltimos, keyinroq qayta urinib ko'ring yoki adminlar bilan bog'laning."
        await message.answer(error_msg)

# --- ADMIN QARORI HANDLING ---
@dp.callback_query(F.data.startswith("ans_"))
async def handle_admin_decision(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    action = parts[1] # ijobiy, zaxira, rad
    target_user_id = parts[2]
    
    # Tracking dan ma'lumotlarni olish
    tracking = getattr(bot, 'anketa_tracking', {})
    if target_user_id not in tracking:
        return await callback.answer("Bu anketa ma'lumotlari topilmadi yoki bot qayta ishga tushgan.", show_alert=True)
    
    messages_to_update = tracking.pop(target_user_id) # Bir martalik qayta ishlash
    
    response_texts = {
        "ijobiy": (
            "✅ <b>Ijobiy</b>\n\n"
            "Hurmatli nomzod!\n\n"
            "Sizning nomzodingiz ko'rib chiqildi va vakansiya talablariga mos deb topildi. "
            "Keyingi bosqichlar bo'yicha ma'lumot berish uchun tez orada siz bilan bog'lanamiz.\n\n"
            "Tasanno Savdo Markazi & Bozorcha Supermarketi\n"
            "HR bo'limi"
        ),
        "zaxira": (
            "🟡 <b>Zaxira</b>\n\n"
            "Hurmatli nomzod!\n\n"
            "Sizning anketangiz ko'rib chiqildi. Hozirgi vaqtda vakansiya bo'yicha tanlov yakunlangan bo'lsa-da, "
            "nomzodingiz istiqbolli deb topildi va zaxira nomzodlar bazasiga kiritildi.\n\n"
            "Kelgusida sizga mos bo'sh ish o'rinlari yuzaga kelganda, albatta siz bilan bog'lanamiz.\n\n"
            "Tasanno Savdo Markazi & Bozorcha Supermarketi\n"
            "HR bo'limi"
        ),
        "rad": (
            "❌ <b>Rad etish</b>\n\n"
            "Hurmatli nomzod!\n\n"
            "Sizning anketangiz ko'rib chiqildi. Afsuski, hozirgi vakansiya bo'yicha nomzodingiz tanlovdan o'tmadi.\n\n"
            "Kompaniyamizga bildirgan qiziqishingiz uchun minnatdorchilik bildiramiz va "
            "kelgusidagi faoliyatingizda muvaffaqiyatlar tilaymiz.\n\n"
            "Tasanno Savdo Markazi & Bozorcha Supermarketi\n"
            "HR bo'limi"
        )
    }
    
    text_to_user = response_texts.get(action)
    status_label = "✅ Ijobiy" if action == "ijobiy" else "🟡 Zaxira" if action == "zaxira" else "❌ Rad etildi"
    
    # Foydalanuvchiga yuborish
    try:
        await bot.send_message(chat_id=target_user_id, text=text_to_user, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Foydalanuvchiga javob yuborishda xatolik: {e}")
        return await callback.answer("Foydalanuvchiga xabar yetib bormadi (botni bloklagan bo'lishi mumkin).", show_alert=True)

    # Barcha adminlardagi tugmalarni yangilash
    for admin_id, msg_id in messages_to_update:
        try:
            await bot.edit_message_reply_markup(chat_id=admin_id, message_id=msg_id, reply_markup=None)
            # Tugmani bosgan adminga status ko'rsatish
            if admin_id == callback.from_user.id:
                await bot.send_message(chat_id=admin_id, text=f"✅ Javob yuborildi: {status_label}")
            else:
                await bot.send_message(chat_id=admin_id, text=f"ℹ️ Ushbu anketa boshqa admin tomonidan ko'rib chiqildi: {status_label}")
        except Exception:
            pass

    await callback.answer("Javob muvaffaqiyatli yuborildi.")

@dp.message(Anketa.photo)
async def photo_fallback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('chosen_lang', 'uz')
    prompt = "Iltimos, faqat rasm yuboring (3x4 yoki selfi):" if lang == 'uz' else "Пожалуйста, отправьте только фото (3х4 или селфи):"
    await message.answer(prompt)

async def main():
    asyncio.create_task(start_web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
