"""Demo content in Persian, Arabic and English.

Medical text is general patient-education material; the clinic should
review and adapt it before going live. Edit everything later in /admin/.
"""

SITE = {
    "clinic_name": ("کلینیک رخسار", "عيادة رخسار", "Rokhsar Clinic"),
    "tagline": (
        "جراحی پلاستیک و زیبایی صورت و بدن، با برنامه‌ریزی دقیق و پیگیری تا یک سال پس از درمان.",
        "جراحة تجميلية للوجه والجسم بتخطيط دقيق ومتابعة لمدة عام كامل بعد العلاج.",
        "Facial and body plastic surgery with careful planning and a full year of follow-up.",
    ),
    "doctor_name": ("دکتر افسون فاضل‌زاده", "الدكتورة أفسون فاضل زاده", "Dr. Afsoon Fazelzadeh"),
    "doctor_title": (
        "متخصص جراحی پلاستیک، ترمیمی و زیبایی",
        "أخصائية جراحة التجميل والترميم",
        "Plastic, reconstructive and aesthetic surgeon",
    ),
    "doctor_bio": (
        "بیشتر مراجعان ما نمی‌خواهند «عمل‌کرده» به نظر برسند؛ می‌خواهند خودشان باشند، با ظاهری آرام‌تر و متناسب‌تر. "
        "رویکرد دکتر فاضل‌زاده ساده است: هر چهره و هر بدن برنامهٔ خودش را دارد و پیش از هر جراحی، همه‌چیز روی کاغذ مشخص می‌شود.\n\n"
        "- عضو انجمن جراحان پلاستیک، ترمیمی و زیبایی ایران\n"
        "- تمرکز بر جراحی بینی، پلک و جوان‌سازی صورت\n"
        "- انجام همهٔ جراحی‌ها در بیمارستان‌های دارای اعتبارنامه\n"
        "- پیگیری شخصی بیمار تا دوازده ماه پس از عمل",
        "معظم مراجعينا لا يريدون أن يبدوا «خاضعين لعملية»؛ يريدون أن يبقوا أنفسهم بمظهر أكثر هدوءاً وتناسقاً. "
        "نهج الدكتورة فاضل زاده بسيط: لكل وجه ولكل جسم خطته الخاصة، وكل شيء يُحدَّد كتابياً قبل أي جراحة.\n\n"
        "- عضوة جمعية جراحي التجميل والترميم الإيرانية\n"
        "- تركيز على تجميل الأنف والجفون وتجديد شباب الوجه\n"
        "- جميع العمليات في مستشفيات معتمدة\n"
        "- متابعة شخصية للمريض حتى اثني عشر شهراً بعد العملية",
        "Most of our patients don't want to look 'done' — they want to look like themselves, only calmer and more balanced. "
        "Dr. Fazelzadeh's approach is simple: every face and body gets its own plan, and everything is agreed in writing before surgery.\n\n"
        "- Member of the Iranian Society of Plastic, Reconstructive and Aesthetic Surgeons\n"
        "- Focus on rhinoplasty, eyelid surgery and facial rejuvenation\n"
        "- All operations performed in accredited hospitals\n"
        "- Personal follow-up for twelve months after surgery",
    ),
    "address": (
        "شیراز، بلوار چمران، ساختمان پزشکان رخسار، طبقهٔ سوم",
        "شيراز، بلوار تشمران، مبنى رخسار الطبي، الطابق الثالث",
        "3rd floor, Rokhsar Medical Building, Chamran Blvd, Shiraz",
    ),
    "working_hours": (
        "شنبه تا چهارشنبه ۱۰ تا ۱۹، پنجشنبه ۱۰ تا ۱۴",
        "السبت إلى الأربعاء 10:00–19:00، الخميس 10:00–14:00",
        "Sat–Wed 10:00–19:00 · Thu 10:00–14:00",
    ),
}

CATEGORIES = [
    # slug, icon, (fa, ar, en)
    ("nose", "nose", ("بینی", "الأنف", "Nose")),
    ("face-neck", "face", ("صورت و گردن", "الوجه والرقبة", "Face & neck")),
    ("eyelids", "eye", ("پلک", "الجفون", "Eyelids")),
    ("body", "body", ("بدن", "الجسم", "Body")),
    ("injectables", "syringe", ("تزریقات و جوان‌سازی", "الحقن والتجديد", "Injectables")),
    ("hair", "hair", ("مو", "الشعر", "Hair")),
]


def T(fa, ar, en):
    return (fa, ar, en)


PROCEDURES = [
    {
        "slug": "rhinoplasty", "category": "nose", "icon": "nose", "surgical": True,
        "title": T("جراحی بینی", "تجميل الأنف", "Rhinoplasty"),
        "summary": T(
            "اصلاح فرم، اندازه و تناسب بینی با چهره — و در صورت نیاز، بهتر کردن تنفس — با حفظ ظاهری طبیعی.",
            "تعديل شكل الأنف وحجمه وتناسبه مع الوجه — وتحسين التنفس عند الحاجة — مع الحفاظ على مظهر طبيعي.",
            "Reshapes the nose to suit your face — and improves breathing when needed — while keeping a natural look.",
        ),
        "intro": T(
            "جراحی بینی (رینوپلاستی) یکی از دقیق‌ترین جراحی‌های زیبایی است. هدف، بینی‌ای است که با پیشانی، گونه‌ها و چانهٔ شما هماهنگ باشد، نه یک «مدل» از پیش تعیین‌شده.\n\n"
            "در این عمل می‌توان قوز بینی را برداشت، نوک افتاده یا پهن را ظریف کرد، پهنای پرهٔ بینی را کم کرد و انحراف تیغه را که روی تنفس اثر می‌گذارد اصلاح کرد.",
            "تجميل الأنف من أدقّ العمليات التجميلية. الهدف أنف يتناغم مع جبهتك ووجنتيك وذقنك، لا «نموذج» جاهز مسبقاً.\n\n"
            "يمكن خلال العملية إزالة حدبة الأنف، وتنحيف الطرف المتدلي أو العريض، وتضييق فتحتي الأنف، وتصحيح انحراف الحاجز الذي يؤثر على التنفس.",
            "Rhinoplasty is one of the most precise cosmetic operations. The goal is a nose that is in harmony with your forehead, cheeks and chin — not a pre-set 'model'.\n\n"
            "It can remove a dorsal hump, refine a drooping or wide tip, narrow the nostrils and straighten a deviated septum that affects breathing.",
        ),
        "duration": T("۲ تا ۴ ساعت", "من ساعتين إلى أربع ساعات", "2–4 hours"),
        "anesthesia": T("بیهوشی عمومی", "تخدير عام", "General anaesthesia"),
        "recovery": T("۷ تا ۱۰ روز", "من 7 إلى 10 أيام", "7–10 days"),
        "longevity": T("دائمی", "دائمة", "Permanent"),
        "meta": T(
            "جراحی بینی در شیراز با طراحی پیش از عمل، دورهٔ نقاهت، عوارض و عکس‌های قبل و بعد. رزرو آنلاین مشاوره.",
            "تجميل الأنف: التخطيط قبل العملية، فترة التعافي، المخاطر وصور قبل وبعد. احجز استشارتك عبر الإنترنت.",
            "Rhinoplasty in Shiraz: planning, recovery, risks and before-and-after photos. Book a consultation online.",
        ),
        "sections": {
            "candidates": T(
                "جراحی بینی برای کسانی مناسب است که رشد صورتشان کامل شده (معمولاً از ۱۷–۱۸ سالگی به بعد)، سالم هستند و انتظار واقع‌بینانه دارند.\n\n"
                "- از فرم یا اندازهٔ بینی خود ناراضی هستید\n- قوز، نوک افتاده یا عدم تقارن دارید\n- انحراف تیغه یا مشکل تنفسی دارید\n- سیگار نمی‌کشید یا می‌توانید چند هفته کنار بگذارید",
                "تناسب عملية تجميل الأنف من اكتمل نمو وجهه (عادةً بعد سن 17–18)، ويتمتع بصحة جيدة وتوقعات واقعية.\n\n"
                "- غير راضٍ عن شكل أنفك أو حجمه\n- لديك حدبة أو طرف متدلٍّ أو عدم تناظر\n- لديك انحراف في الحاجز أو صعوبة في التنفس\n- لا تدخن أو تستطيع التوقف لعدة أسابيع",
                "Rhinoplasty suits people whose face has finished growing (usually from 17–18), who are in good health and have realistic expectations.\n\n"
                "- You are unhappy with the shape or size of your nose\n- You have a hump, a drooping tip or asymmetry\n- You have a deviated septum or breathing problems\n- You don't smoke, or can stop for several weeks",
            ),
            "consultation": T(
                "در جلسهٔ مشاوره، دکتر بینی را از داخل و خارج معاینه می‌کند، از چهرهٔ شما در زاویه‌های استاندارد عکس می‌گیرد و دربارهٔ هدفتان صحبت می‌کند. "
                "سابقهٔ پزشکی، داروها، حساسیت‌ها و جراحی‌های قبلی بررسی می‌شود. در پایان، برنامهٔ مکتوب درمان، هزینه و زمان‌بندی را دریافت می‌کنید.",
                "في جلسة الاستشارة تفحص الطبيبة الأنف من الداخل والخارج، وتلتقط صوراً لوجهك من زوايا قياسية، وتتحدث معك عن هدفك. "
                "تُراجَع السوابق الطبية والأدوية والحساسية والعمليات السابقة. وفي النهاية تحصل على خطة علاج مكتوبة مع التكلفة والجدول الزمني.",
                "At the consultation the doctor examines your nose inside and out, takes standard photos and talks through what you want to change. "
                "Your medical history, medicines, allergies and previous surgery are reviewed. You leave with a written treatment plan, the cost and a timeline.",
            ),
            "questions": T(
                "- آیا من کاندید مناسبی برای این جراحی هستم؟\n- چه تغییری برای چهرهٔ من واقع‌بینانه است؟\n- روش باز است یا بسته، و چرا؟\n- عمل در کدام بیمارستان انجام می‌شود؟\n- در صورت نیاز به ترمیم، برنامه چیست؟",
                "- هل أنا مرشح مناسب لهذه العملية؟\n- ما التغيير الواقعي بالنسبة لوجهي؟\n- هل التقنية مفتوحة أم مغلقة، ولماذا؟\n- في أي مستشفى ستُجرى العملية؟\n- ما الخطة إذا احتجت إلى تعديل لاحقاً؟",
                "- Am I a good candidate for this operation?\n- What change is realistic for my face?\n- Will you use an open or closed technique, and why?\n- In which hospital will it be done?\n- What happens if I need a revision?",
            ),
            "preparation": T(
                "دو هفته پیش از عمل، آسپرین، ایبوپروفن، مکمل‌های گیاهی و ویتامین E را قطع کنید (مگر به دستور پزشک). سیگار را دست‌کم چهار هفته کنار بگذارید. "
                "آزمایش‌های لازم انجام می‌شود و برای روز عمل و ۲۴ ساعت اول، یک همراه داشته باشید.",
                "قبل أسبوعين من العملية أوقف الأسبرين والإيبوبروفين والمكملات العشبية وفيتامين E (إلا بأمر الطبيب). وتوقف عن التدخين أربعة أسابيع على الأقل. "
                "تُجرى التحاليل اللازمة، ورتّب لمرافق يوم العملية وخلال أول 24 ساعة.",
                "Stop aspirin, ibuprofen, herbal supplements and vitamin E two weeks before surgery (unless your doctor says otherwise). Stop smoking for at least four weeks. "
                "Routine tests are done beforehand, and you'll need someone with you on the day and for the first 24 hours.",
            ),
            "procedure": T(
                "- بیهوشی عمومی توسط متخصص بیهوشی\n- برش داخل بینی (بسته) یا برش کوچک زیر ستون بینی (باز)\n- اصلاح استخوان و غضروف بر اساس طرح از پیش تعیین‌شده\n- اصلاح تیغهٔ بینی در صورت نیاز برای تنفس بهتر\n- بستن برش‌ها و گذاشتن آتل روی بینی",
                "- تخدير عام بإشراف طبيب تخدير\n- شق داخل الأنف (مغلقة) أو شق صغير تحت عمود الأنف (مفتوحة)\n- تعديل العظم والغضروف وفق الخطة المسبقة\n- تصحيح الحاجز عند الحاجة لتنفس أفضل\n- إغلاق الشقوق ووضع جبيرة على الأنف",
                "- General anaesthesia given by an anaesthetist\n- Incisions inside the nose (closed) or a small cut under the columella (open)\n- Bone and cartilage reshaped to the agreed plan\n- Septum straightened if needed for better breathing\n- Incisions closed and a splint placed on the nose",
            ),
            "recovery": T(
                "آتل بعد از حدود یک هفته برداشته می‌شود. تورم و کبودی دور چشم در دو هفتهٔ اول بیشتر است و کم‌کم از بین می‌رود. "
                "بیشتر افراد بعد از ۷ تا ۱۰ روز به کار برمی‌گردند؛ ورزش سنگین تا ۶ هفته ممنوع است. تورم ظریف نوک بینی ممکن است تا یک سال کامل طول بکشد.",
                "تُزال الجبيرة بعد نحو أسبوع. يكون التورم والكدمات حول العينين أوضح في الأسبوعين الأولين ثم يزولان تدريجياً. "
                "يعود معظم الأشخاص إلى العمل بعد 7–10 أيام، ويُمنع التمرين الشاق لمدة 6 أسابيع. قد يستمر تورم بسيط في طرف الأنف حتى عام كامل.",
                "The splint comes off after about a week. Swelling and bruising around the eyes peak in the first two weeks and then fade. "
                "Most people return to work after 7–10 days; strenuous exercise is off-limits for 6 weeks. Subtle swelling of the tip can take up to a year to settle.",
            ),
            "risks": T(
                "هر جراحی خطراتی دارد. در جلسهٔ مشاوره دربارهٔ آن‌ها صحبت می‌کنیم و رضایت‌نامهٔ آگاهانه امضا می‌شود.\n\n"
                "- خونریزی و عفونت\n- عوارض بیهوشی\n- بی‌حسی یا تغییر رنگ موقت پوست\n- عدم تقارن یا نتیجه‌ای که نیاز به ترمیم دارد\n- مشکل تنفسی",
                "لكل جراحة مخاطر. نناقشها في جلسة الاستشارة ويُوقَّع إقرار موافقة مستنيرة.\n\n"
                "- نزيف وعدوى\n- مضاعفات التخدير\n- خدر أو تغير مؤقت في لون الجلد\n- عدم تناظر أو نتيجة تحتاج إلى تعديل\n- صعوبة في التنفس",
                "Every operation carries risks. We go through them at the consultation and you sign an informed-consent form.\n\n"
                "- Bleeding and infection\n- Anaesthesia complications\n- Temporary numbness or skin discoloration\n- Asymmetry or a result that needs revision\n- Breathing difficulty",
            ),
            "results": T(
                "نتیجهٔ اولیه بعد از برداشتن آتل دیده می‌شود، اما فرم نهایی بینی بعد از ۹ تا ۱۲ ماه شکل می‌گیرد. نتیجه دائمی است، هرچند با افزایش سن چهره کمی تغییر می‌کند.",
                "تظهر النتيجة الأولية بعد إزالة الجبيرة، أما الشكل النهائي فيتكوّن بعد 9–12 شهراً. النتيجة دائمة، مع تغيّر طفيف في الوجه مع التقدم في العمر.",
                "You'll see an early result when the splint comes off, but the final shape settles over 9–12 months. The result is permanent, though the face naturally changes a little with age.",
            ),
        },
        "faqs": [
            T("جراحی بینی درد دارد؟", "هل عملية تجميل الأنف مؤلمة؟", "Is rhinoplasty painful?"),
            T(
                "بیشتر بیماران «احساس گرفتگی» را بیشتر از درد توصیف می‌کنند. درد چند روز اول با مسکن‌های معمولی کنترل می‌شود.",
                "يصف معظم المرضى شعوراً «بالانسداد» أكثر من الألم. يُسيطر على ألم الأيام الأولى بمسكنات عادية.",
                "Most patients describe feeling 'blocked up' rather than pain. Discomfort in the first few days is managed with ordinary painkillers.",
            ),
            T("چه زمانی می‌توانم عینک بزنم؟", "متى يمكنني ارتداء النظارات؟", "When can I wear glasses?"),
            T(
                "تا حدود ۶ هفته عینک نباید مستقیماً روی بینی فشار بیاورد. در این مدت از لنز یا روش‌های نگه‌داشتن عینک روی پیشانی استفاده کنید.",
                "يجب ألا تضغط النظارات مباشرة على الأنف لمدة 6 أسابيع تقريباً. استخدم العدسات اللاصقة أو طرقاً لتعليقها على الجبهة خلال هذه الفترة.",
                "Glasses shouldn't rest directly on the nose for about 6 weeks. Use contact lenses or tape them to your forehead in the meantime.",
            ),
        ],
    },
    {
        "slug": "facelift", "category": "face-neck", "icon": "face", "surgical": True,
        "title": T("لیفت صورت و گردن", "شدّ الوجه والرقبة", "Facelift and neck lift"),
        "summary": T(
            "کاهش افتادگی گونه‌ها، خط فک و گردن با جابه‌جایی لایه‌های عمقی؛ چهره‌ای جوان‌تر بدون حالت کشیده.",
            "تقليل ترهّل الخدين وخط الفك والرقبة بإعادة تموضع الطبقات العميقة؛ وجه أكثر شباباً دون مظهر مشدود.",
            "Lifts sagging cheeks, jawline and neck by repositioning the deeper layers — younger, without a 'pulled' look.",
        ),
        "intro": T(
            "با افزایش سن، بافت‌های صورت پایین می‌آیند و خط فک و زاویهٔ گردن محو می‌شود. لیفت صورت به جای کشیدن پوست، لایهٔ عضلانی–بافتی زیر آن را به جای اصلی‌اش برمی‌گرداند؛ به همین دلیل نتیجه طبیعی‌تر و ماندگارتر است.",
            "مع التقدم في العمر تنزل أنسجة الوجه ويختفي خط الفك وزاوية الرقبة. شدّ الوجه لا يشدّ الجلد فقط، بل يعيد الطبقة العضلية النسيجية تحته إلى مكانها؛ لذا تكون النتيجة أكثر طبيعية واستدامة.",
            "With age, facial tissues descend and the jawline and neck angle soften. Rather than pulling the skin, a facelift returns the muscle-tissue layer beneath it to where it was — which is why the result looks more natural and lasts longer.",
        ),
        "duration": T("۳ تا ۵ ساعت", "من 3 إلى 5 ساعات", "3–5 hours"),
        "anesthesia": T("بیهوشی عمومی", "تخدير عام", "General anaesthesia"),
        "recovery": T("۲ تا ۳ هفته", "من أسبوعين إلى ثلاثة", "2–3 weeks"),
        "longevity": T("۸ تا ۱۰ سال", "من 8 إلى 10 سنوات", "8–10 years"),
        "meta": T("لیفت صورت و گردن: روش انجام، نقاهت، عوارض و نتایج.", "شد الوجه والرقبة: الإجراء والتعافي والمخاطر والنتائج.", "Facelift and neck lift: how it's done, recovery, risks and results."),
        "sections": {
            "candidates": T(
                "- افتادگی گونه و ایجاد غبغب یا «جول»\n- شل شدن پوست و نوارهای عضلانی گردن\n- سلامت عمومی خوب و عدم مصرف سیگار",
                "- ترهّل الخدين وظهور «الغبغب»\n- ارتخاء الجلد وأشرطة عضلات الرقبة\n- صحة عامة جيدة وعدم التدخين",
                "- Sagging cheeks and jowls\n- Loose skin and visible bands in the neck\n- Good general health and not smoking",
            ),
            "procedure": T(
                "برش‌ها در امتداد خط مو و پشت گوش قرار می‌گیرند تا بعداً دیده نشوند. لایهٔ عمقی بالا برده و ثابت می‌شود، پوست اضافه برداشته و بدون کشش دوخته می‌شود.",
                "توضع الشقوق على طول خط الشعر وخلف الأذن كي لا تُرى لاحقاً. تُرفع الطبقة العميقة وتُثبَّت، ويُزال الجلد الزائد ويُخاط دون شدّ.",
                "Incisions follow the hairline and run behind the ear so they are hidden later. The deep layer is lifted and secured, excess skin removed and closed without tension.",
            ),
            "recovery": T(
                "تورم و کبودی در هفتهٔ اول بیشتر است. بخیه‌ها بعد از ۷ تا ۱۰ روز کشیده می‌شوند و بیشتر افراد بعد از ۲ تا ۳ هفته در جمع حاضر می‌شوند.",
                "يكون التورم والكدمات أشد في الأسبوع الأول. تُزال الغرز بعد 7–10 أيام، ويعود معظم الأشخاص إلى الأماكن العامة بعد 2–3 أسابيع.",
                "Swelling and bruising are most noticeable in the first week. Stitches come out after 7–10 days and most people feel ready to be seen in public after 2–3 weeks.",
            ),
            "risks": T(
                "- هماتوم (تجمع خون)\n- آسیب موقت عصب و بی‌حسی\n- جای زخم\n- ریزش موقت مو کنار برش",
                "- ورم دموي\n- إصابة مؤقتة في العصب وخدر\n- ندبات\n- تساقط مؤقت للشعر بجانب الشق",
                "- Haematoma (a collection of blood)\n- Temporary nerve injury and numbness\n- Scarring\n- Temporary hair loss near the incision",
            ),
        },
        "faqs": [],
    },
    {
        "slug": "eyelid-surgery", "category": "eyelids", "icon": "eye", "surgical": True,
        "title": T("جراحی پلک", "جراحة الجفون", "Eyelid surgery"),
        "summary": T(
            "برداشتن پوست و چربی اضافهٔ پلک بالا یا پف زیر چشم برای نگاهی بازتر و سرحال‌تر.",
            "إزالة الجلد والدهون الزائدة من الجفن العلوي أو انتفاخ ما تحت العين لنظرة أكثر انفتاحاً وحيوية.",
            "Removes excess skin and fat from the upper lids or under-eye bags for a more open, rested look.",
        ),
        "intro": T(
            "افتادگی پوست پلک بالا می‌تواند چشم را خسته نشان دهد و گاهی حتی میدان دید را محدود کند. پف زیر چشم هم معمولاً با خواب و کرم برطرف نمی‌شود. بلفاروپلاستی این مشکلات را با برش‌هایی که در چین طبیعی پلک پنهان می‌شود اصلاح می‌کند.",
            "قد يجعل ترهّل جلد الجفن العلوي العين تبدو متعبة، وأحياناً يحدّ من مجال الرؤية. ولا تزول انتفاخات ما تحت العين عادةً بالنوم أو الكريمات. يصحح رأب الجفن ذلك بشقوق تختفي في ثنية الجفن الطبيعية.",
            "Hooded upper lids can make the eyes look tired and sometimes even limit your field of vision. Under-eye bags rarely respond to sleep or creams. Blepharoplasty corrects both through incisions hidden in the natural lid crease.",
        ),
        "duration": T("۱ تا ۲ ساعت", "من ساعة إلى ساعتين", "1–2 hours"),
        "anesthesia": T("بی‌حسی موضعی با آرام‌بخش", "تخدير موضعي مع مهدئ", "Local anaesthesia with sedation"),
        "recovery": T("۷ تا ۱۰ روز", "من 7 إلى 10 أيام", "7–10 days"),
        "longevity": T("سال‌ها؛ پلک بالا معمولاً بیش از ۱۰ سال", "سنوات؛ الجفن العلوي عادة أكثر من 10 سنوات", "Many years; upper lids often 10+"),
        "meta": T("جراحی پلک بالا و پایین: کاندیدها، نقاهت و عوارض.", "جراحة الجفن العلوي والسفلي: المرشحون والتعافي والمخاطر.", "Upper and lower eyelid surgery: candidates, recovery and risks."),
        "sections": {
            "candidates": T(
                "- پوست اضافه روی پلک بالا\n- پف یا کیسهٔ چربی زیر چشم\n- نداشتن بیماری فعال چشم یا خشکی شدید چشم",
                "- جلد زائد على الجفن العلوي\n- انتفاخ أو أكياس دهنية تحت العين\n- عدم وجود مرض نشط في العين أو جفاف شديد",
                "- Excess skin on the upper lids\n- Puffiness or fat bags under the eyes\n- No active eye disease or severe dry eye",
            ),
            "procedure": T(
                "در پلک بالا برش در چین طبیعی پلک ایجاد می‌شود. در پلک پایین، برش زیر مژه‌ها یا از داخل پلک است. چربی برداشته یا جابه‌جا و پوست اضافه برداشته می‌شود.",
                "في الجفن العلوي يكون الشق في الثنية الطبيعية. وفي السفلي تحت الرموش أو من داخل الجفن. تُزال الدهون أو يُعاد توزيعها ويُزال الجلد الزائد.",
                "Upper-lid incisions sit in the natural crease. Lower-lid incisions are just below the lashes or inside the lid. Fat is removed or repositioned and excess skin trimmed.",
            ),
            "recovery": T(
                "کمپرس سرد در ۴۸ ساعت اول تورم را کم می‌کند. بخیه‌ها حدود روز پنجم کشیده می‌شوند. آرایش چشم و لنز را دو هفته کنار بگذارید.",
                "تقلل الكمادات الباردة في أول 48 ساعة التورم. تُزال الغرز في اليوم الخامس تقريباً. تجنّب مكياج العين والعدسات لمدة أسبوعين.",
                "Cold compresses in the first 48 hours reduce swelling. Stitches come out around day five. Avoid eye make-up and contact lenses for two weeks.",
            ),
            "risks": T(
                "- خشکی یا سوزش موقت چشم\n- تاری دید موقت\n- عدم تقارن جزئی\n- مشکل در بستن کامل پلک (نادر)",
                "- جفاف أو حرقة مؤقتة في العين\n- تشوش مؤقت في الرؤية\n- عدم تناظر طفيف\n- صعوبة في إغلاق الجفن بالكامل (نادر)",
                "- Temporary dry or irritated eyes\n- Temporary blurred vision\n- Slight asymmetry\n- Difficulty closing the eyes fully (rare)",
            ),
        },
        "faqs": [],
    },
    {
        "slug": "liposuction", "category": "body", "icon": "body", "surgical": True,
        "title": T("لیپوساکشن", "شفط الدهون", "Liposuction"),
        "summary": T(
            "برداشتن چربی‌های مقاوم به رژیم و ورزش در شکم، پهلو، ران یا بازو برای فرمی متناسب‌تر.",
            "إزالة الدهون المقاومة للحمية والرياضة في البطن والخصر والفخذين أو الذراعين لقوام أكثر تناسقاً.",
            "Removes diet-resistant fat from the abdomen, flanks, thighs or arms for a more balanced shape.",
        ),
        "intro": T(
            "لیپوساکشن روش کاهش وزن نیست؛ برای اصلاح فرم بدن در نواحی‌ای است که با وجود وزن مناسب، چربی در آن‌ها باقی می‌ماند. نتیجهٔ خوب به کیفیت پوست و ثبات وزن پس از عمل بستگی دارد.",
            "شفط الدهون ليس وسيلة لإنقاص الوزن؛ بل لتحسين شكل الجسم في مناطق تبقى فيها الدهون رغم الوزن المناسب. تعتمد النتيجة الجيدة على جودة الجلد وثبات الوزن بعد العملية.",
            "Liposuction is not a weight-loss method; it reshapes areas where fat stays despite a healthy weight. A good result depends on skin quality and keeping your weight stable afterwards.",
        ),
        "duration": T("۱ تا ۳ ساعت", "من ساعة إلى 3 ساعات", "1–3 hours"),
        "anesthesia": T("بیهوشی عمومی یا بی‌حسی", "تخدير عام أو موضعي", "General or local anaesthesia"),
        "recovery": T("۵ تا ۷ روز", "من 5 إلى 7 أيام", "5–7 days"),
        "longevity": T("دائمی با ثبات وزن", "دائمة مع ثبات الوزن", "Permanent if weight is stable"),
        "meta": T("لیپوساکشن: کاندیدها، روش، گن پس از عمل و عوارض.", "شفط الدهون: المرشحون، الإجراء، المشد بعد العملية والمخاطر.", "Liposuction: candidates, technique, compression garments and risks."),
        "sections": {
            "candidates": T(
                "- وزن نزدیک به وزن ایده‌آل\n- پوست با کشسانی خوب\n- چربی موضعی مقاوم به رژیم و ورزش",
                "- وزن قريب من الوزن المثالي\n- جلد بمرونة جيدة\n- دهون موضعية مقاومة للحمية والرياضة",
                "- Weight close to your ideal\n- Skin with good elasticity\n- Localised fat that resists diet and exercise",
            ),
            "procedure": T(
                "از برش‌های چندمیلی‌متری، محلول بی‌حسی تزریق و سپس چربی با کانول‌های ظریف خارج می‌شود. بلافاصله پس از عمل گن طبی پوشیده می‌شود.",
                "عبر شقوق صغيرة بضعة مليمترات يُحقن محلول مخدر ثم تُشفط الدهون بقنيات دقيقة. يُلبس مشدّ طبي مباشرة بعد العملية.",
                "Through incisions a few millimetres long, a numbing solution is injected and fat removed with fine cannulas. A compression garment goes on straight after surgery.",
            ),
            "recovery": T(
                "گن طبی ۴ تا ۶ هفته پوشیده می‌شود. پیاده‌روی از روز اول توصیه می‌شود. نتیجهٔ نهایی بعد از ۳ ماه با فروکش کامل تورم دیده می‌شود.",
                "يُرتدى المشد الطبي 4–6 أسابيع. يُنصح بالمشي من اليوم الأول. تظهر النتيجة النهائية بعد 3 أشهر مع زوال التورم.",
                "The compression garment is worn for 4–6 weeks. Walking from day one is encouraged. The final result shows at about 3 months once swelling settles.",
            ),
            "risks": T(
                "- ناهمواری سطح پوست\n- تجمع مایع (سروما)\n- بی‌حسی موقت\n- لخته شدن خون (نادر)",
                "- عدم انتظام سطح الجلد\n- تجمّع السوائل\n- خدر مؤقت\n- جلطات دموية (نادرة)",
                "- Uneven skin contour\n- Fluid collection (seroma)\n- Temporary numbness\n- Blood clots (rare)",
            ),
        },
        "faqs": [],
    },
    {
        "slug": "tummy-tuck", "category": "body", "icon": "body", "surgical": True,
        "title": T("جراحی شکم (ابدومینوپلاستی)", "شدّ البطن", "Tummy tuck"),
        "summary": T(
            "برداشتن پوست اضافه و ترمیم دیوارهٔ عضلانی شکم پس از بارداری یا کاهش وزن زیاد.",
            "إزالة الجلد الزائد وإصلاح جدار البطن العضلي بعد الحمل أو فقدان الوزن الكبير.",
            "Removes loose skin and repairs the abdominal muscles after pregnancy or major weight loss.",
        ),
        "intro": T(
            "بارداری یا کاهش وزن زیاد می‌تواند پوست شکم را شل و عضلات را از هم دور کند؛ مشکلی که با ورزش برطرف نمی‌شود. ابدومینوپلاستی پوست اضافه را برمی‌دارد و عضلات را دوباره کنار هم می‌دوزد.",
            "قد يؤدي الحمل أو فقدان الوزن الكبير إلى ترهّل جلد البطن وتباعد العضلات، وهي مشكلة لا تحلها الرياضة. يزيل شدّ البطن الجلد الزائد ويعيد خياطة العضلات.",
            "Pregnancy or major weight loss can leave loose skin and separated muscles that exercise can't fix. A tummy tuck removes the excess skin and stitches the muscles back together.",
        ),
        "duration": T("۲ تا ۴ ساعت", "من ساعتين إلى أربع", "2–4 hours"),
        "anesthesia": T("بیهوشی عمومی", "تخدير عام", "General anaesthesia"),
        "recovery": T("۲ تا ۴ هفته", "من أسبوعين إلى أربعة", "2–4 weeks"),
        "longevity": T("دائمی با ثبات وزن", "دائمة مع ثبات الوزن", "Permanent if weight is stable"),
        "meta": T("ابدومینوپلاستی: کاندیدها، نقاهت و عوارض.", "شد البطن: المرشحون والتعافي والمخاطر.", "Tummy tuck: candidates, recovery and risks."),
        "sections": {
            "candidates": T(
                "- پوست شل و آویزان شکم\n- جدا شدن عضلات شکم پس از بارداری\n- برنامه نداشتن برای بارداری دوباره",
                "- جلد بطن مترهّل\n- تباعد عضلات البطن بعد الحمل\n- عدم التخطيط لحمل جديد",
                "- Loose, overhanging abdominal skin\n- Separated abdominal muscles after pregnancy\n- No plans for another pregnancy",
            ),
            "procedure": T(
                "برش افقی پایین شکم (زیر خط لباس زیر) زده می‌شود، عضلات ترمیم و پوست اضافه برداشته می‌شود. ناف در جای طبیعی خود بازسازی می‌شود.",
                "يُجرى شق أفقي أسفل البطن (تحت خط الملابس الداخلية)، وتُصلح العضلات ويُزال الجلد الزائد، ويُعاد تشكيل السرة في مكانها الطبيعي.",
                "A horizontal incision is made low on the abdomen (below the underwear line), the muscles are repaired and excess skin removed. The navel is reshaped in its natural position.",
            ),
            "recovery": T(
                "چند روز اول کمی خمیده راه می‌روید. گن طبی ۶ هفته پوشیده می‌شود و بلند کردن اجسام سنگین تا ۶ هفته ممنوع است.",
                "تمشي منحنياً قليلاً في الأيام الأولى. يُرتدى المشد 6 أسابيع ويُمنع حمل الأشياء الثقيلة لمدة 6 أسابيع.",
                "You'll walk slightly bent for the first few days. A compression garment is worn for 6 weeks and heavy lifting is off-limits for 6 weeks.",
            ),
            "risks": T(
                "- جای زخم پهن\n- سروما\n- تأخیر در ترمیم زخم\n- لخته شدن خون (نادر)",
                "- ندبة عريضة\n- تجمع السوائل\n- تأخر التئام الجرح\n- جلطات دموية (نادرة)",
                "- A wide scar\n- Seroma\n- Delayed wound healing\n- Blood clots (rare)",
            ),
        },
        "faqs": [],
    },
    {
        "slug": "dermal-fillers", "category": "injectables", "icon": "lips", "surgical": False,
        "title": T("تزریق فیلر", "حقن الفيلر", "Dermal fillers"),
        "summary": T(
            "حجم‌دهی ملایم به لب، گونه و خط فک یا پر کردن خطوط عمیق، بدون جراحی و با زمان استراحت کوتاه.",
            "إضافة حجم لطيف للشفاه والوجنتين وخط الفك أو ملء الخطوط العميقة دون جراحة وبفترة راحة قصيرة.",
            "Gently restores volume to lips, cheeks and jawline or softens deep lines — no surgery, little downtime.",
        ),
        "intro": T(
            "فیلرهای هیالورونیک اسید ماده‌ای مشابه ترکیبات طبیعی پوست دارند و به تدریج جذب بدن می‌شوند. هدف ما «پرکردن» نیست، بازگرداندن تناسب از دست‌رفته است؛ به همین دلیل معمولاً مقدار کمتری از آنچه انتظار دارید تزریق می‌شود.",
            "تحتوي فيلرات حمض الهيالورونيك على مادة مشابهة لمكونات الجلد الطبيعية وتمتصها الجسم تدريجياً. هدفنا ليس «الملء» بل استعادة التناسب المفقود؛ لذلك نحقن عادةً كمية أقل مما تتوقع.",
            "Hyaluronic-acid fillers are similar to substances naturally found in the skin and are gradually absorbed. Our aim isn't to 'fill' but to restore lost proportion — so we usually inject less than you might expect.",
        ),
        "duration": T("۳۰ تا ۴۵ دقیقه", "من 30 إلى 45 دقيقة", "30–45 minutes"),
        "anesthesia": T("کرم بی‌حسی", "كريم مخدر", "Numbing cream"),
        "recovery": T("همان روز", "في اليوم نفسه", "Same day"),
        "longevity": T("۶ تا ۱۸ ماه", "من 6 إلى 18 شهراً", "6–18 months"),
        "meta": T("تزریق فیلر لب، گونه و خط فک: ماندگاری و مراقبت‌ها.", "حقن الفيلر للشفاه والوجنتين وخط الفك: المدة والرعاية.", "Lip, cheek and jawline fillers: how long they last and aftercare."),
        "sections": {
            "candidates": T(
                "- لب‌های کم‌حجم یا نامتقارن\n- گودی زیر چشم یا کاهش حجم گونه\n- نداشتن بارداری، شیردهی یا عفونت فعال پوست",
                "- شفاه رفيعة أو غير متناظرة\n- تجويف تحت العين أو فقدان حجم الوجنتين\n- عدم وجود حمل أو رضاعة أو عدوى جلدية نشطة",
                "- Thin or uneven lips\n- Hollows under the eyes or flattened cheeks\n- Not pregnant, breastfeeding or with an active skin infection",
            ),
            "procedure": T(
                "پس از طراحی و کرم بی‌حسی، فیلر با سوزن ظریف یا کانول تزریق و ماساژ داده می‌شود. نتیجه بلافاصله دیده می‌شود.",
                "بعد التخطيط ووضع الكريم المخدر، يُحقن الفيلر بإبرة دقيقة أو قنية ثم يُدلَّك. تظهر النتيجة فوراً.",
                "After planning and numbing cream, filler is injected with a fine needle or cannula and gently moulded. You see the result straight away.",
            ),
            "recovery": T(
                "تورم خفیف یک تا سه روز طول می‌کشد. ۲۴ ساعت ورزش سنگین، سونا و آرایش سنگین ممنوع است.",
                "يستمر تورم خفيف من يوم إلى ثلاثة. تجنّب الرياضة الشاقة والساونا والمكياج الثقيل لمدة 24 ساعة.",
                "Mild swelling lasts one to three days. Avoid strenuous exercise, saunas and heavy make-up for 24 hours.",
            ),
            "risks": T(
                "- کبودی و تورم\n- برجستگی یا ناهمواری\n- انسداد عروقی (نادر اما جدی؛ به همین دلیل تزریق فقط توسط پزشک انجام می‌شود)",
                "- كدمات وتورم\n- كتل أو عدم انتظام\n- انسداد وعائي (نادر لكنه خطير؛ لذلك لا يحقن إلا الطبيب)",
                "- Bruising and swelling\n- Lumps or unevenness\n- Vascular occlusion (rare but serious — which is why only a doctor injects)",
            ),
        },
        "faqs": [
            T("اگر از نتیجه راضی نباشم چه؟", "ماذا لو لم تعجبني النتيجة؟", "What if I don't like the result?"),
            T(
                "فیلرهای هیالورونیک با آنزیم مخصوص قابل حل شدن هستند. در جلسهٔ کنترل دو هفته بعد، نتیجه را با هم بررسی می‌کنیم.",
                "يمكن إذابة فيلرات الهيالورونيك بإنزيم خاص. نراجع النتيجة معاً في جلسة المتابعة بعد أسبوعين.",
                "Hyaluronic fillers can be dissolved with a specific enzyme. We review the result together at a check-up two weeks later.",
            ),
        ],
    },
    {
        "slug": "botulinum-toxin", "category": "injectables", "icon": "syringe", "surgical": False,
        "title": T("تزریق بوتاکس", "حقن البوتوكس", "Botulinum toxin"),
        "summary": T(
            "نرم کردن خطوط پیشانی، بین ابرو و دور چشم با حفظ حالت طبیعی چهره.",
            "تنعيم خطوط الجبهة وبين الحاجبين وحول العينين مع الحفاظ على تعابير الوجه الطبيعية.",
            "Softens forehead lines, frown lines and crow's feet while keeping natural expression.",
        ),
        "intro": T(
            "بوتولینوم توکسین فعالیت عضلات کوچک صورت را به‌طور موقت کم می‌کند تا خطوط ناشی از حرکت نرم شوند. با دوز درست، چهره همچنان حالت دارد — فقط آرام‌تر به نظر می‌رسد.",
            "يقلل البوتولينوم نشاط عضلات الوجه الصغيرة مؤقتاً لتنعيم خطوط الحركة. بالجرعة الصحيحة يبقى الوجه معبّراً — لكنه يبدو أكثر هدوءاً.",
            "Botulinum toxin temporarily relaxes small facial muscles so expression lines soften. At the right dose your face still moves — it just looks more relaxed.",
        ),
        "duration": T("۱۵ تا ۲۰ دقیقه", "من 15 إلى 20 دقيقة", "15–20 minutes"),
        "anesthesia": T("نیاز ندارد", "لا حاجة", "None needed"),
        "recovery": T("همان روز", "في اليوم نفسه", "Same day"),
        "longevity": T("۳ تا ۴ ماه", "من 3 إلى 4 أشهر", "3–4 months"),
        "meta": T("تزریق بوتاکس: نواحی درمان، ماندگاری و مراقبت‌ها.", "حقن البوتوكس: المناطق، المدة والرعاية.", "Botulinum toxin: treatment areas, how long it lasts and aftercare."),
        "sections": {
            "candidates": T(
                "- خطوط پیشانی و اخم\n- چین‌های دور چشم\n- نداشتن بارداری، شیردهی یا بیماری‌های عصبی–عضلانی",
                "- خطوط الجبهة والعبوس\n- تجاعيد حول العين\n- عدم وجود حمل أو رضاعة أو أمراض عصبية عضلية",
                "- Forehead and frown lines\n- Crow's feet\n- Not pregnant, breastfeeding or with neuromuscular disease",
            ),
            "procedure": T(
                "نقاط تزریق روی چهره علامت‌گذاری و دارو با سوزن بسیار ظریف تزریق می‌شود. اثر از روز سوم شروع و تا روز چهاردهم کامل می‌شود.",
                "تُحدَّد نقاط الحقن ويُحقن الدواء بإبرة دقيقة جداً. يبدأ التأثير في اليوم الثالث ويكتمل بحلول اليوم الرابع عشر.",
                "Injection points are marked and the medicine injected with a very fine needle. It starts working around day three and is complete by day fourteen.",
            ),
            "recovery": T(
                "تا ۴ ساعت دراز نکشید و ناحیه را ماساژ ندهید. ورزش سنگین را تا روز بعد کنار بگذارید.",
                "لا تستلقِ ولا تدلّك المنطقة لمدة 4 ساعات. تجنّب الرياضة الشاقة حتى اليوم التالي.",
                "Don't lie down or rub the area for 4 hours. Skip strenuous exercise until the next day.",
            ),
            "risks": T(
                "- کبودی کوچک محل تزریق\n- سردرد خفیف\n- افتادگی موقت ابرو یا پلک (نادر)",
                "- كدمة صغيرة مكان الحقن\n- صداع خفيف\n- تدلٍّ مؤقت للحاجب أو الجفن (نادر)",
                "- Small bruise at the injection site\n- Mild headache\n- Temporary brow or lid droop (rare)",
            ),
        },
        "faqs": [],
    },
    {
        "slug": "hair-transplant", "category": "hair", "icon": "hair", "surgical": True,
        "title": T("کاشت مو", "زراعة الشعر", "Hair transplant"),
        "summary": T(
            "انتقال فولیکول‌های مو از پشت سر به نواحی کم‌پشت یا طاس، با خط رویش طبیعی.",
            "نقل بصيلات الشعر من مؤخرة الرأس إلى المناطق الخفيفة أو الصلعاء بخط منبت طبيعي.",
            "Moves hair follicles from the back of the head to thinning or bald areas with a natural hairline.",
        ),
        "intro": T(
            "در کاشت مو، فولیکول‌ها از ناحیهٔ پشت سر که در برابر ریزش مقاوم است برداشته و در ناحیهٔ کم‌پشت کاشته می‌شوند. در روش FUE فولیکول‌ها تک‌تک برداشته می‌شوند و جای بخیهٔ خطی باقی نمی‌ماند.",
            "في زراعة الشعر تُؤخذ البصيلات من مؤخرة الرأس المقاومة للتساقط وتُزرع في المنطقة الخفيفة. في تقنية FUE تُستخرج البصيلات واحدة تلو الأخرى دون ندبة خطية.",
            "In a hair transplant, follicles are taken from the back of the scalp — which resists hair loss — and placed where hair is thin. With FUE they are removed one by one, leaving no linear scar.",
        ),
        "duration": T("۵ تا ۸ ساعت", "من 5 إلى 8 ساعات", "5–8 hours"),
        "anesthesia": T("بی‌حسی موضعی", "تخدير موضعي", "Local anaesthesia"),
        "recovery": T("۷ تا ۱۰ روز", "من 7 إلى 10 أيام", "7–10 days"),
        "longevity": T("دائمی", "دائمة", "Permanent"),
        "meta": T("کاشت مو به روش FUE: کاندیدها، مراحل رشد و نقاهت.", "زراعة الشعر بتقنية FUE: المرشحون ومراحل النمو والتعافي.", "FUE hair transplant: candidates, growth timeline and recovery."),
        "sections": {
            "candidates": T(
                "- ریزش مو با الگوی ثابت\n- ناحیهٔ دهندهٔ پشت سر با تراکم کافی\n- انتظار واقع‌بینانه از تراکم نهایی",
                "- تساقط شعر بنمط مستقر\n- منطقة مانحة بكثافة كافية\n- توقعات واقعية للكثافة النهائية",
                "- Hair loss with a stable pattern\n- Enough density in the donor area\n- Realistic expectations about final density",
            ),
            "procedure": T(
                "خط رویش با توجه به فرم صورت طراحی می‌شود. فولیکول‌ها برداشت، شمارش و در شیارهای ریز با زاویهٔ طبیعی کاشته می‌شوند.",
                "يُصمَّم خط المنبت وفق شكل الوجه. تُستخرج البصيلات وتُعدّ وتُزرع في شقوق دقيقة بزاوية طبيعية.",
                "The hairline is designed to suit your face. Follicles are harvested, counted and placed in tiny slits at a natural angle.",
            ),
            "recovery": T(
                "دلمه‌ها تا روز دهم می‌ریزند. موهای کاشته‌شده در هفته‌های ۲ تا ۶ می‌ریزند و از ماه سوم رشد تازه شروع می‌شود؛ نتیجهٔ کامل ۱۲ ماه بعد است.",
                "تسقط القشور بحلول اليوم العاشر. يتساقط الشعر المزروع بين الأسبوع 2 و6 ويبدأ النمو الجديد من الشهر الثالث؛ والنتيجة الكاملة بعد 12 شهراً.",
                "Scabs fall off by day ten. Transplanted hairs shed in weeks 2–6 and new growth starts from month three; the full result shows at 12 months.",
            ),
            "risks": T(
                "- تورم پیشانی در روزهای اول\n- خارش و فولیکولیت\n- تراکم کمتر از انتظار",
                "- تورم الجبهة في الأيام الأولى\n- حكة والتهاب البصيلات\n- كثافة أقل من المتوقع",
                "- Forehead swelling in the first days\n- Itching and folliculitis\n- Lower density than hoped",
            ),
        },
        "faqs": [],
    },
]

GENERAL_FAQS = [
    (
        T("آیا جلسهٔ مشاوره هزینه دارد؟", "هل للاستشارة رسوم؟", "Is there a fee for the consultation?"),
        T(
            "بله، هزینهٔ ویزیت مشاوره هنگام مراجعه پرداخت می‌شود و در صورت انجام جراحی، از هزینهٔ عمل کسر می‌شود. ثبت درخواست نوبت در سایت رایگان است.",
            "نعم، تُدفع رسوم الاستشارة عند الحضور وتُخصم من تكلفة العملية إذا أُجريت. تقديم طلب الموعد عبر الموقع مجاني.",
            "Yes — the consultation fee is paid at the visit and deducted from the surgery cost if you go ahead. Requesting an appointment online is free.",
        ),
    ),
    (
        T("بعد از ثبت درخواست چه اتفاقی می‌افتد؟", "ماذا يحدث بعد تقديم الطلب؟", "What happens after I request an appointment?"),
        T(
            "منشی در همان روز کاری با شما تماس می‌گیرد، زمان را تأیید می‌کند و مدارکی را که باید همراه بیاورید می‌گوید.",
            "تتصل بك السكرتيرة في يوم العمل نفسه لتأكيد الموعد وإخبارك بالمستندات التي يجب إحضارها.",
            "The secretary calls you the same working day to confirm the time and tell you what to bring.",
        ),
    ),
    (
        T("آیا جراحی توسط خود دکتر انجام می‌شود؟", "هل تُجري الطبيبة العملية بنفسها؟", "Does the doctor perform the surgery personally?"),
        T(
            "بله. همان پزشکی که طرح درمان را با شما بررسی می‌کند، جراحی را انجام می‌دهد و پیگیری‌ها را شخصاً انجام می‌دهد.",
            "نعم. الطبيبة التي تراجع خطة العلاج معك هي من تُجري العملية وتتابعك شخصياً.",
            "Yes. The doctor who plans your treatment with you performs the operation and sees you at every follow-up.",
        ),
    ),
    (
        T("از بیماران خارج از کشور هم پذیرش دارید؟", "هل تستقبلون مرضى من خارج البلاد؟", "Do you accept patients from abroad?"),
        T(
            "بله. مشاورهٔ اولیه آنلاین انجام می‌شود و برای اقامت و برنامهٔ سفر کنار شما هستیم. حداقل اقامت پس از جراحی بینی ۱۰ روز است.",
            "نعم. تُجرى الاستشارة الأولى عبر الإنترنت ونساعدك في الإقامة وخطة السفر. الحد الأدنى للإقامة بعد تجميل الأنف 10 أيام.",
            "Yes. The first consultation can be online and we help with accommodation and travel plans. Plan to stay at least 10 days after rhinoplasty.",
        ),
    ),
    (
        T("عکس‌های قبل و بعد واقعی هستند؟", "هل صور قبل وبعد حقيقية؟", "Are the before-and-after photos real?"),
        T(
            "عکس‌ها فقط با رضایت کتبی بیمار منتشر می‌شوند و جز برش و تنظیم نور، ویرایشی روی آن‌ها انجام نمی‌شود.",
            "لا تُنشر الصور إلا بموافقة خطية من المريض، ولا يُجرى عليها أي تعديل سوى القص وضبط الإضاءة.",
            "Photos are published only with the patient's written consent and are not edited beyond cropping and light correction.",
        ),
    ),
]

CASES = [
    # slug image prefix, procedure slug, title, caption, months, hero
    ("rhino-hump", "rhinoplasty",
     T("برداشتن قوز و اصلاح نوک بینی", "إزالة حدبة الأنف وتعديل الطرف", "Hump removal and tip refinement"),
     T("تصویر نمونه · روش باز", "صورة توضيحية · تقنية مفتوحة", "Sample illustration · open technique"), 12, True),
    ("rhino-tip", "rhinoplasty",
     T("بالا آوردن نوک افتادهٔ بینی", "رفع طرف الأنف المتدلي", "Lifting a drooping tip"),
     T("تصویر نمونه · روش بسته", "صورة توضيحية · تقنية مغلقة", "Sample illustration · closed technique"), 9, False),
    ("neck-lift", "facelift",
     T("لیفت گردن و خط فک", "شد الرقبة وخط الفك", "Neck and jawline lift"),
     T("تصویر نمونه · لیفت لایهٔ عمقی", "صورة توضيحية · شد الطبقة العميقة", "Sample illustration · deep-plane lift"), 6, False),
    ("eyelid", "eyelid-surgery",
     T("جراحی پلک بالا", "جراحة الجفن العلوي", "Upper eyelid surgery"),
     T("تصویر نمونه · بی‌حسی موضعی", "صورة توضيحية · تخدير موضعي", "Sample illustration · local anaesthesia"), 3, False),
    ("body", "liposuction",
     T("لیپوساکشن شکم و پهلو", "شفط دهون البطن والخصر", "Abdomen and flank liposuction"),
     T("تصویر نمونه · همراه با گن طبی", "صورة توضيحية · مع مشد طبي", "Sample illustration · with compression garment"), 6, False),
    ("lips", "dermal-fillers",
     T("حجم‌دهی ملایم لب", "إضافة حجم لطيف للشفاه", "Subtle lip volume"),
     T("تصویر نمونه · ۱ میلی‌لیتر فیلر", "صورة توضيحية · 1 مل فيلر", "Sample illustration · 1 ml filler"), 1, False),
]

TESTIMONIALS = [
    ("مریم ک.", "rhinoplasty", T(
        "از جلسهٔ اول، دکتر دقیق گفت چه چیزی برای صورت من شدنی است و چه چیزی نه. همین صداقت باعث شد اعتماد کنم. حالا بعد از یک سال، کسی متوجه نمی‌شود عمل کرده‌ام؛ فقط می‌گویند سرحال‌تر شده‌ام.",
        "منذ الجلسة الأولى قالت الطبيبة بدقة ما هو ممكن لوجهي وما ليس ممكناً. هذه الصراحة جعلتني أثق بها. الآن بعد عام لا يلاحظ أحد أنني أجريت عملية؛ يقولون فقط إنني أبدو أكثر حيوية.",
        "From the first visit the doctor told me exactly what was possible for my face and what wasn't. That honesty is why I trusted her. A year on, nobody can tell I had surgery — they just say I look fresher.",
    ), 12),
    ("علی ر.", "hair-transplant", T(
        "منشی کلینیک تمام مراحل را از قبل توضیح داد و حتی بعد از عمل چند بار تماس گرفت. ماه نهم هستم و نتیجه از چیزی که فکر می‌کردم طبیعی‌تر است.",
        "شرحت السكرتيرة جميع المراحل مسبقاً واتصلت عدة مرات بعد العملية. أنا الآن في الشهر التاسع والنتيجة أكثر طبيعية مما توقعت.",
        "The secretary explained every step beforehand and even called a few times after the procedure. I'm nine months in and it looks more natural than I expected.",
    ), 9),
    ("Sara M.", "eyelid-surgery", T(
        "از عراق برای جراحی پلک آمدم. مشاورهٔ آنلاین، هماهنگی اقامت و پیگیری بعد از برگشت همه منظم بود. چشم‌هایم دیگر خسته به نظر نمی‌رسند.",
        "جئت من العراق لجراحة الجفون. الاستشارة عبر الإنترنت وترتيب الإقامة والمتابعة بعد عودتي كانت كلها منظمة. عيناي لم تعودا تبدوان متعبتين.",
        "I travelled from Iraq for eyelid surgery. The online consultation, accommodation and follow-up after I got home were all well organised. My eyes don't look tired any more.",
    ), 3),
]
