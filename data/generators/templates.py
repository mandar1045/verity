"""Message template families for the synthetic dataset.

TEMPLATES[class][lang] is a list of body patterns. Each body is one "template
family"; the train/val/test split is done by family, so the test set only
contains phrasings the model never saw. Slots like {amt} are filled by
gen_messages.py with synthetic values. All names, numbers and links are fake.
"""

SCAM_CLASSES = (
    "COLLECT_REFUND", "QR_RECEIVE", "FAKE_KYC", "OTP_THEFT", "REMOTE_ACCESS", "FAKE_CARE",
    "TASK_JOB", "PRIZE", "WRONG_TRANSFER", "BILL_DISCONNECT", "VIT_PHISH", "FAMILY_IMPERSONATION",
)
LEGIT_CLASSES = (
    "BANK_ALERT", "BANK_OTP", "MERCHANT_RECEIPT", "AUTOPAY_NOTICE", "COLLEGE_NOTICE",
    "DELIVERY_UPDATE", "PROMO", "PERSONAL_CHAT", "CASUAL_CHAT",
)
# CASUAL_CHAT was added after the v1 external check: with only structured legit
# messages, the model learned "conversational = scam" and flagged ~49% of
# everyday UCI chats. These bodies are written from scratch, not taken from UCI.

TEMPLATES: dict[str, dict[str, list[str]]] = {
    # ------------------------------------------------------------------ scams
    "COLLECT_REFUND": {
        "en": [
            "Your refund of {amt} for order #{order} has been approved. Accept the collect request from {vpa} and enter your UPI PIN to receive the amount.",
            "{brand} Refund Desk: {amt} cashback is pending. To receive it, approve the payment request sent to your UPI app and enter PIN.",
            "Sir, I am from {brand} support. We have sent a request of {amt} to your UPI. Just click Pay and put your PIN, money will be credited in 2 mins.",
            "Your electricity overcharge refund of {amt} is ready. Approve the collect request in {upi_app} within {hours} hours to get the refund.",
            "Income tax refund {amt} sanctioned. Kindly accept request from {vpa} and enter UPI PIN to receive refund in your account.",
            "Dear user, failed transaction amount {amt} will be reversed only after you accept the collect request and authorise it with your UPI PIN.",
            "Hi, your insurance claim {amt} is processed. You will get a request on {upi_app}, approve it with PIN so the amount gets credited.",
            "{brand}: Order cancelled. Refund {amt} initiated. Tap Pay on the request from {vpa} and enter MPIN to claim your refund today.",
        ],
        "hinglish": [
            "Aapka refund {amt} approve ho gaya hai. Collect request accept karke PIN daalo, paise turant milenge.",
            "Sir {brand} se bol raha hoon, {amt} cashback ke liye request bheji hai, bas UPI PIN daal do, amount credit ho jayega.",
            "Refund {amt} pending hai. {upi_app} me jo request aayi hai usko approve karo aur PIN enter karo, paisa aa jayega.",
            "Aapka paisa wapas aa raha hai {amt}, payment request pe pay dabao aur pin daalo receive karne ke liye.",
        ],
        "hi": [
            "आपका {amt} का रिफंड मंज़ूर हो गया है। कलेक्ट रिक्वेस्ट स्वीकार करें और पैसे पाने के लिए UPI पिन डालें।",
            "{brand} रिफंड: {amt} आपके खाते में क्रेडिट होगा, बस भेजी गई रिक्वेस्ट पर पिन दर्ज करें।",
            "प्रिय ग्राहक, {amt} वापसी के लिए अपने UPI ऐप में अनुरोध स्वीकार करें और पिन डालें, पैसे तुरंत मिलेंगे।",
        ],
        "ta": [
            "உங்கள் {amt} ரீஃபண்ட் அங்கீகரிக்கப்பட்டது. பணம் பெற கலெக்ட் கோரிக்கையை ஏற்று UPI PIN உள்ளிடவும்.",
            "{brand} ரீஃபண்ட் {amt} தயார். உங்கள் UPI செயலியில் வந்த கோரிக்கையில் பின் எண் போட்டால் பணம் கிடைக்கும்.",
        ],
    },
    "QR_RECEIVE": {
        "en": [
            "Hi, I am interested in your {item} on OLX. I have sent a QR code, scan it to receive {amt} advance payment.",
            "Buyer here for your {item}. Scan the attached QR and enter UPI PIN to receive {amt} in your account.",
            "Army officer here, I will buy your {item} for {amt}. Scanning my QR is the only way to receive the money, please scan and approve.",
            "Payment of {amt} for your {item} is ready. Scan this code with {upi_app} to get the money instantly.",
            "Sir please scan the QR I sent on WhatsApp, enter PIN and {amt} will be credited to you for the {item}.",
            "Your cashback of {amt} is waiting. Scan the QR below to receive the cashback directly in your bank.",
            "To receive your OLX payment of {amt}, scan the QR code and confirm with your UPI PIN.",
            "Got your ad for the {item}. I paid {amt} through QR, just scan and put pin to accept it.",
        ],
        "hinglish": [
            "Bhai aapka {item} lena hai, maine QR bheja hai, scan karo aur {amt} receive karo.",
            "Advance {amt} bhej raha hoon, QR scan karke PIN daalo paise aa jayenge.",
            "OLX pe aapka {item} pasand aaya. Payment ke liye ye QR scan kariye, {amt} aapke account me credit ho jayega.",
            "Sir QR code scan karo aur pin dalo, tabhi {amt} milega aapko.",
        ],
        "hi": [
            "आपके {item} के लिए {amt} भेज रहा हूँ, यह क्यूआर स्कैन करें और पैसे पाने के लिए पिन डालें।",
            "भुगतान प्राप्त करने के लिए भेजा गया क्यूआर कोड स्कैन करें, {amt} तुरंत मिलेंगे।",
            "सर, OLX वाले {item} का एडवांस {amt} है, क्यूआर स्कैन करके पिन डालिए।",
        ],
        "ta": [
            "உங்கள் {item}க்கு {amt} அனுப்புகிறேன். இந்த QR-ஐ ஸ்கேன் செய்து பணம் பெற PIN உள்ளிடவும்.",
            "பணம் கிடைக்க நான் அனுப்பிய QR குறியீட்டை ஸ்கேன் செய்யுங்கள், {amt} உடனே வரவு வைக்கப்படும்.",
        ],
    },
    "FAKE_KYC": {
        "en": [
            "Dear Customer, your {bank} account will be blocked today. Update your KYC immediately at {bad_link}",
            "{bank_short} ALERT: Your PAN is not linked. Account suspended in {hours} hrs. Complete e-KYC now: {bad_link}",
            "Your {bank} NetBanking access is on hold due to pending KYC. Verify details here {bad_link} to avoid deactivation.",
            "Dear user, as per RBI guidelines your KYC has expired. Click {bad_link} and update Aadhaar to continue using UPI.",
            "Your {upi_app} wallet will be deactivated tonight. Re-KYC required. Visit {bad_link}",
            "Final notice: {bank} a/c {acct} KYC pending. Update before {time} or a penalty of Rs 500 applies. {bad_link}",
            "Your SIM will be blocked in 24 hours due to incomplete KYC. Call our executive at {phone} or update at {bad_link}",
            "{bank}: Debit card frozen. Update KYC through the secure link {short} to unfreeze.",
        ],
        "hinglish": [
            "Priya grahak, aapka {bank_short} account aaj band ho jayega. Turant KYC update karo: {bad_link}",
            "Aapka PAN link nahi hai, account block ho jayega. Abhi yahan KYC pura karein {bad_link}",
            "{bank_short}: KYC expire ho gaya hai. 24 ghante me update karein warna UPI band. {short}",
            "Dear customer aapka wallet suspend ho jayega, KYC update kijiye {bad_link} par jaldi.",
        ],
        "hi": [
            "प्रिय ग्राहक, आपका {bank} खाता आज बंद हो जाएगा। तुरंत केवाईसी अपडेट करें: {bad_link}",
            "आपका पैन लिंक नहीं है। 24 घंटे में KYC पूरा करें वरना खाता ब्लॉक हो जाएगा। {bad_link}",
            "{bank}: आपकी केवाईसी समाप्त हो गई है, खाता निलंबित होगा। यहाँ अपडेट करें {short}",
        ],
        "ta": [
            "அன்புள்ள வாடிக்கையாளரே, உங்கள் {bank} கணக்கு இன்று முடக்கப்படும். உடனே KYC புதுப்பிக்கவும்: {bad_link}",
            "உங்கள் பான் இணைக்கப்படவில்லை. 24 மணி நேரத்தில் கேஒய்சி செய்யாவிட்டால் கணக்கு மூடப்படும். {bad_link}",
        ],
    },
    "OTP_THEFT": {
        "en": [
            "Share the OTP sent to your number to confirm your {amt} cashback.",
            "Hi, this is {name} from {brand}. You will get a 6 digit code now, please tell me the code to verify your order refund.",
            "Your {brand} reward of {amt} is ready. Reply with the OTP you received to credit it.",
            "Sir, by mistake I entered your number for OTP. Please forward the code you just got, it is urgent.",
            "{bank} verification: to stop the unauthorised transaction of {amt}, send us the OTP received on your mobile.",
            "Congratulations! Your credit card limit is increased. Provide the OTP to our agent to activate it.",
            "Your gas subsidy {amt} is pending. Share the OTP with the officer on call to receive it.",
            "Dear customer, confirm your identity by giving the verification code sent to you. Do not delay or the account will be locked.",
        ],
        "hinglish": [
            "Aapke number pe ek OTP aaya hoga, woh batao cashback {amt} ke liye.",
            "Sir order verify karna hai, jo OTP aaya hai please bhej do jaldi.",
            "Bhai galti se mera OTP tumhare number pe aa gaya, please bata do.",
            "{bank_short} se bol raha hoon, transaction rokne ke liye OTP share karo abhi.",
        ],
        "hi": [
            "आपके नंबर पर आया ओटीपी बताएं, ताकि {amt} का कैशबैक मिल सके।",
            "सर, ऑर्डर कन्फर्म करने के लिए जो ओटीपी आया है वह भेजें।",
            "बैंक से बोल रहा हूँ, गलत लेनदेन रोकने के लिए ओटीपी शेयर करें।",
        ],
        "ta": [
            "உங்கள் {amt} கேஷ்பேக் உறுதிப்படுத்த, வந்த OTP-ஐ பகிரவும்.",
            "சார், ஆர்டர் சரிபார்க்க உங்களுக்கு வந்த ஓடிபி எண்ணை சொல்லுங்கள்.",
        ],
    },
    "REMOTE_ACCESS": {
        "en": [
            "Install AnyDesk from Play Store, our executive will fix your refund in 5 minutes.",
            "{bank} support: to resolve the failed payment of {amt}, download {app} and share the 9-digit code.",
            "Your UPI is not working due to a server issue. Install the QuickSupport app and our team will update it remotely.",
            "Sir, please open TeamViewer and tell me the ID, I will process your {brand} refund from my side.",
            "To get your cashback install the {brand} Helper app from {bad_apk} and allow all permissions.",
            "Customer care here. Turn on screen sharing in the app so I can guide you to receive {amt}.",
            "Your KYC can be done online only. Download RustDesk and keep the call on while our officer completes it.",
            "Refund failed 3 times. Our executive will connect to your phone through AirDroid, please install it now.",
        ],
        "hinglish": [
            "Aapka refund atka hai, AnyDesk download karo, humara executive sab kar dega.",
            "Sir TeamViewer install kijiye aur code bataiye, payment issue solve ho jayega.",
            "Screen share karo please, main aapko step by step refund receive karna sikhata hoon.",
            "QuickSupport app daalo phone me, hum remotely aapka KYC kar denge.",
        ],
        "hi": [
            "आपका रिफंड अटका है, एनीडेस्क ऐप डाउनलोड करें, हमारे अधिकारी सब ठीक कर देंगे।",
            "भुगतान समस्या हल करने के लिए टीमव्यूअर इंस्टॉल करें और कोड बताएं।",
            "स्क्रीन शेयर चालू करें, हम आपको {amt} पाने में मदद करेंगे।",
        ],
        "ta": [
            "உங்கள் ரீஃபண்ட் நிலுவையில் உள்ளது. AnyDesk நிறுவுங்கள், எங்கள் அதிகாரி சரி செய்வார்.",
            "பணம் பெற திரை பகிர்வு இயக்கி, எங்கள் ஊழியருக்கு குறியீட்டை சொல்லுங்கள்.",
        ],
    },
    "FAKE_CARE": {
        "en": [
            "Your payment of {amt} to {merchant} failed. Call customer care at {phone} for an immediate refund.",
            "{brand} Customer Care: complaint #{order} registered. Contact our executive on {phone} to process the refund.",
            "Transaction declined. For help call our 24x7 helpline {phone} (toll free).",
            "Dear user, your {upi_app} account has an issue. Speak to the support team on {phone} now.",
            "Hello, we saw your tweet about the failed payment. Our {bank_short} officer will help, WhatsApp {phone}.",
            "Your complaint against {merchant} is escalated. Call senior manager {name} at {phone} to get {amt} back.",
            "{brand} helpdesk: double debit of {amt} detected. Dial {phone} to reverse it within 24 hrs.",
            "For a refund of the electricity bill paid twice, contact the customer care executive at {phone}.",
        ],
        "hinglish": [
            "Aapka {amt} ka payment fail hua hai. Refund ke liye customer care {phone} pe call karo.",
            "{brand} support: complaint register ho gayi, executive se {phone} pe baat karein.",
            "Payment atak gaya? Turant helpline {phone} par call kijiye.",
            "Sir aapka paisa double kat gaya, wapas lene ke liye {phone} pe sampark karein.",
        ],
        "hi": [
            "आपका {amt} का भुगतान विफल हुआ। रिफंड के लिए कस्टमर केयर {phone} पर कॉल करें।",
            "शिकायत दर्ज हो गई है। अधिकारी से {phone} पर संपर्क करें।",
            "दोहरा भुगतान हुआ है, पैसे वापस पाने के लिए {phone} पर फोन करें।",
        ],
        "ta": [
            "உங்கள் {amt} கட்டணம் தோல்வியடைந்தது. ரீஃபண்ட் பெற வாடிக்கையாளர் சேவை {phone} அழைக்கவும்.",
            "புகார் பதிவு செய்யப்பட்டது. எங்கள் அதிகாரியை {phone} இல் தொடர்பு கொள்ளவும்.",
        ],
    },
    "TASK_JOB": {
        "en": [
            "Earn {amt_day} per day by liking YouTube videos. Pay {amt_small} registration fee to start. WhatsApp {phone}",
            "Part-time job offer: rate hotels on Google Maps and earn up to {amt_day} daily. Join our Telegram for tasks.",
            "Hi, I am {name} from an HR agency. Work from home 30 mins a day, salary {amt_day}/day. Deposit {amt_small} to unlock your first task.",
            "Your profile is selected for a {brand} online job. Complete 3 prepaid tasks and withdraw the profit instantly.",
            "Earn daily by reviewing products. Today's bonus task: invest {amt_small}, get {amt} back in 1 hour.",
            "Home based typing job, earn {amt_day} weekly. Pay a one-time joining fee of {amt_small}.",
            "Like 10 posts, earn {amt_day}. To withdraw your earnings pay a small tax of {amt_small} first.",
            "Students wanted: data entry from mobile, {amt_day}/day guaranteed. Activation charge {amt_small} only.",
        ],
        "hinglish": [
            "Ghar baithe kamaye {amt_day} roz, bas videos like karo. Registration fee {amt_small} bhejo.",
            "Part time job hai, roz {amt_day} kamaiye. Pehle {amt_small} jama karo task unlock karne ke liye.",
            "Telegram task join karo, har like pe paise milenge. Activation ke liye {amt_small} pay karo.",
            "Students ke liye mobile job, {amt_day} daily. Bas {amt_small} joining fee dijiye.",
        ],
        "hi": [
            "घर बैठे रोज़ {amt_day} कमाएं, बस वीडियो लाइक करें। पहले {amt_small} रजिस्ट्रेशन फीस भेजें।",
            "पार्ट टाइम नौकरी: रोज़ {amt_day} कमाइए, काम शुरू करने के लिए {amt_small} पंजीकरण शुल्क दें।",
            "मोबाइल से काम करें और कमाएं। पहला टास्क खोलने के लिए {amt_small} जमा करें।",
        ],
        "ta": [
            "வீட்டிலிருந்தே தினமும் {amt_day} சம்பாதியுங்கள். வீடியோ லைக் செய்தால் போதும். பதிவு கட்டணம் {amt_small} செலுத்தவும்.",
            "பகுதி நேர வேலை: தினமும் {amt_day} சம்பாதிக்கலாம். முதலில் {amt_small} கட்டணம் அனுப்பவும்.",
        ],
    },
    "PRIZE": {
        "en": [
            "Congratulations! You have won {amt_big} in the {brand} lucky draw. Pay {amt_small} processing fee to claim.",
            "KBC Lottery: your number won {amt_big}. Contact manager {name} at {phone} to release your prize.",
            "You are our lucky customer of the month! Claim your free iPhone at {bad_link}",
            "Dear winner, your {brand} reward of {amt_big} is pending. Pay GST of {amt_small} to receive it.",
            "Your mobile number has been selected for a cash prize of {amt_big}. Reply YES and pay the delivery charge.",
            "Jackpot! {amt_big} added to your reward wallet. Unlock it by paying {amt_small} at {short}",
            "{brand} anniversary gift: you are 1 of 10 winners. Verify at {bad_link} within 24 hours.",
            "Your scratch card worth {amt_big} expires today. Claim your reward now: {short}",
        ],
        "hinglish": [
            "Badhai ho! Aapne {brand} lucky draw me {amt_big} jeeta hai. Processing fee {amt_small} bhejo.",
            "Aapka number lottery me select hua, inaam {amt_big}. Claim karne ke liye {phone} pe call karo.",
            "Lucky draw me aapka naam aaya hai, iPhone jeeta hai. {bad_link} par details bharo.",
            "Aapka inaam {amt_big} ready hai, bas GST {amt_small} pay karo abhi.",
        ],
        "hi": [
            "बधाई हो! आपने {brand} लकी ड्रॉ में {amt_big} जीता है। प्रोसेसिंग फीस {amt_small} भेजें।",
            "आपका नंबर लॉटरी में चुना गया है, इनाम {amt_big}। दावा करने के लिए {phone} पर कॉल करें।",
            "आपको इनाम मिला है! {short} पर जाकर तुरंत दावा करें।",
        ],
        "ta": [
            "வாழ்த்துக்கள்! {brand} அதிர்ஷ்ட குலுக்கலில் {amt_big} வென்றுள்ளீர்கள். செயலாக்க கட்டணம் {amt_small} செலுத்தவும்.",
            "உங்கள் எண்ணுக்கு லாட்டரி பரிசு {amt_big}. பெற {phone} அழைக்கவும்.",
        ],
    },
    "WRONG_TRANSFER": {
        "en": [
            "Hi, I sent {amt} to your number by mistake. Please return it, I have sent a request on {upi_app}.",
            "Sorry, I mistakenly transferred {amt} to you. Kindly accept the request I raised to return the money.",
            "Bro {amt} went to your UPI wrongly, it was my hospital fee. Please send it back to {vpa} urgently.",
            "Madam, my son paid {amt} to your account by mistake. Please approve my collect request, God bless you.",
            "You must have got a credit SMS of {amt}. That was wrongly sent by me, return it to {vpa} please.",
            "Hello, check your account, {amt} came from me by mistake. I am a student, please return it quickly.",
            "Wrong transfer of {amt} to your number. Scan my QR and send it back, I will pay 100 extra.",
            "I accidentally sent you {amt} instead of my brother. Please refund it through the payment request.",
        ],
        "hinglish": [
            "Bhaiya galti se {amt} aapke number pe chala gaya, please wapas bhej do.",
            "Maine galti se {amt} bhej diye, request bheji hai, accept kar do please.",
            "Sorry galat number par {amt} transfer ho gaya, {vpa} pe wapas kar do.",
            "Aapke account me {amt} aaye honge mere, galti se gaye, return kar dijiye jaldi.",
        ],
        "hi": [
            "मैंने गलती से {amt} आपके नंबर पर भेज दिए, कृपया वापस भेज दें।",
            "गलती से पैसे आपके खाते में गए हैं, मेरी रिक्वेस्ट स्वीकार करके {amt} वापस करें।",
            "भाई साहब, {amt} गलत नंबर पर चले गए, कृपया लौटा दीजिए।",
        ],
        "ta": [
            "தவறுதலாக {amt} உங்கள் எண்ணுக்கு அனுப்பிவிட்டேன். தயவுசெய்து திருப்பி அனுப்புங்கள்.",
            "நான் அனுப்பிய {amt} தவறுதலாக உங்களுக்கு வந்தது, என் கோரிக்கையை ஏற்று திருப்பி அனுப்பவும்.",
        ],
    },
    "BILL_DISCONNECT": {
        "en": [
            "Dear consumer, your electricity will be disconnected tonight at {time} as last month's bill is not updated. Call officer {phone}.",
            "{eb}: Power supply to your house will be cut today at {time}. Contact the electricity officer {phone} immediately.",
            "Your electricity bill of {amt} is unpaid. To avoid disconnection, pay now at {bad_link}",
            "EB notice: meter update pending. Connection will be cut within 2 hours. WhatsApp {phone}",
            "Dear customer, your gas connection will be suspended tomorrow. Update the payment by calling {phone}",
            "Final warning: electricity supply stops at {time}. Download the {eb} app from {bad_apk} to pay.",
            "Your power bill payment failed. Disconnection tonight. Our lineman {name} will help, call {phone}",
            "Previous month bill not received. Pay {amt} to {vpa} within 1 hour to keep your supply on.",
        ],
        "hinglish": [
            "Aapki bijli aaj raat {time} baje kat jayegi, bill update nahi hai. Officer ko {phone} pe call karo.",
            "Light connection cut ho jayega, turant {phone} par baat karein.",
            "Bijli bill {amt} pending hai, abhi {bad_link} par pay karo warna connection band.",
            "EB office se: meter update karna hai, 2 ghante me bijli kat jayegi, call karein {phone}",
        ],
        "hi": [
            "प्रिय उपभोक्ता, आपकी बिजली आज रात {time} बजे काट दी जाएगी। तुरंत बिजली अधिकारी को {phone} पर कॉल करें।",
            "आपका बिजली बिल {amt} बकाया है। कनेक्शन कट जाएगी, अभी {bad_link} पर भुगतान करें।",
            "बिजली विभाग: मीटर अपडेट नहीं है, आज ही {phone} पर संपर्क करें।",
        ],
        "ta": [
            "உங்கள் மின் இணைப்பு இன்றிரவு {time}க்கு துண்டிக்கப்படும். உடனே மின் வாரிய அதிகாரியை {phone} அழைக்கவும்.",
            "மின் கட்டணம் {amt} நிலுவையில் உள்ளது. இன்றே {bad_link} இல் செலுத்தவும்.",
        ],
    },
    "VIT_PHISH": {
        "en": [
            "Dear Student, your VTOP account is suspended due to unusual activity. Verify your credentials at {vit_bad} within 24 hours.",
            "VIT IT Helpdesk: your mailbox has exceeded its quota. Login at {vit_bad} to keep receiving emails.",
            "Your hostel fee payment failed. Re-enter your VTOP login and card details at {vit_bad} before the deadline.",
            "Important: CAT results are withheld. Confirm your registration number and password at {vit_bad}",
            "Dear {name}, your scholarship of {amt} is approved. Submit your bank details on {vit_bad} to receive it.",
            "VTOP password expires today. Update it now to avoid account lock: {vit_bad}",
            "Exam hall ticket blocked due to pending dues. Pay {amt} immediately at {vit_bad}",
            "VIT Placement Cell: you are shortlisted. Register with your VTOP credentials at {vit_bad}",
        ],
        "hinglish": [
            "VTOP account block ho gaya hai, turant {vit_bad} par login karke verify karo.",
            "Hostel fee fail hui, VTOP password aur card details {vit_bad} pe daalo aaj hi.",
            "Scholarship {amt} approve hua, bank details {vit_bad} pe submit karo jaldi.",
            "Bhai VIT IT team ka mail aaya, password expire ho raha hai, {vit_bad} pe update karo.",
        ],
        "hi": [
            "प्रिय छात्र, आपका VTOP खाता निलंबित है। 24 घंटे में {vit_bad} पर पासवर्ड सत्यापित करें।",
            "VIT हेल्पडेस्क: आपकी हॉस्टल फीस असफल रही, {vit_bad} पर लॉगिन करें।",
            "आपकी स्कॉलरशिप {amt} मंज़ूर हुई, बैंक विवरण {vit_bad} पर भेजें।",
        ],
        "ta": [
            "அன்புள்ள மாணவரே, உங்கள் VTOP கணக்கு முடக்கப்படும். உடனே {vit_bad} இல் கடவுச்சொல்லை உறுதிப்படுத்தவும்.",
            "உங்கள் உதவித்தொகை {amt} அங்கீகரிக்கப்பட்டது. வங்கி விவரங்களை {vit_bad} இல் சமர்ப்பிக்கவும்.",
        ],
    },
    "FAMILY_IMPERSONATION": {
        "en": [
            "Hi Mom, this is my new number. Phone fell in water. Need {amt} urgently, send to {vpa} please.",
            "Hey it's me {name}, using a friend's phone. Stuck at the hospital, send {amt} to this UPI right now, will explain later.",
            "Papa my old SIM is not working, save this new number. Pay my exam fee of {amt} today to {vpa}.",
            "Hi, new number. Can you transfer {amt} quickly? My bank app is not working, I will return it tonight.",
            "Uncle, this is {name}'s friend, he met with an accident. Send {amt} immediately for the treatment to {vpa}.",
            "It's me, don't call, I am in a meeting. Need you to pay {amt} to this vendor UPI {vpa} asap.",
            "Didi this is my new WhatsApp. Urgent, send {amt} for my hostel deposit, will give it back on Sunday.",
            "Hi, I am your cousin {name}, lost my wallet in Delhi. Please GPay {amt} to {vpa}, very urgent.",
        ],
        "hinglish": [
            "Mummy ye mera naya number hai, purana kharab ho gaya. Turant {amt} bhej do {vpa} pe.",
            "Bhai main hoon {name}, naya number hai. Hospital me hoon, abhi {amt} bhej do please.",
            "Papa phone kho gaya, ye naya number save karo. Exam fee {amt} aaj hi bhejo.",
            "Didi jaldi se {amt} bhej do is UPI pe, baad me batata hoon, call mat karna.",
        ],
        "hi": [
            "माँ, यह मेरा नया नंबर है। तुरंत {amt} इस UPI पर भेज दो।",
            "भैया, मैं {name} हूँ, नया नंबर है। अस्पताल में हूँ, अभी पैसे भेजो।",
            "पापा, फोन खो गया। मेरा नया नंबर सेव करो और आज ही {amt} भेज दो।",
        ],
        "ta": [
            "அம்மா, இது என் புதிய எண். அவசரமாக {amt} இந்த UPI-க்கு அனுப்புங்கள்.",
            "அண்ணா, நான் {name}, புதிய எண். மருத்துவமனையில் இருக்கிறேன், உடனே பணம் அனுப்புங்கள்.",
        ],
    },
    # ------------------------------------------------------------- legitimate
    "BANK_ALERT": {
        "en": [
            "{bank_short}: Rs {amt_n} debited from A/c {acct} on {date} to VPA {vpa_m}. Not you? Call {tollfree} -{bank_short}",
            "Dear Customer, INR {amt_n} credited to your A/c {acct} on {date} by UPI ref {ref}. Avl bal INR {bal}. -{bank}",
            "{bank}: Your A/c {acct} is debited by Rs.{amt_n} for {merchant} on {date}. If not done by you, report at {tollfree}.",
            "UPI txn of Rs {amt_n} to {name} successful. Ref No {ref}. Balance: Rs {bal}. - {bank_short}",
            "Your card ending {card4} was used for Rs {amt_n} at {merchant} on {date}. Not you? Block it in the {bank_short} app.",
            "{bank}: Salary of INR {amt_big_n} credited to A/c {acct} on {date}.",
            "Alert: Your {bank_short} Debit Card has been blocked as requested. For a new card, visit the branch or use the official app.",
            "Rs {amt_n} received from {name} via UPI on {date}. Updated balance Rs {bal}. -{bank_short}",
        ],
        "hinglish": [
            "Aapke A/c {acct} se Rs {amt_n} debit hue {date} ko. Aapne nahi kiya? {tollfree} par call karein. -{bank_short}",
            "Rs {amt_n} aapke khate me credit ho gaye. UPI Ref {ref}. -{bank_short}",
            "{bank_short}: UPI se Rs {amt_n} {merchant} ko bheje gaye. Balance Rs {bal}.",
            "Aapka {bank_short} card {merchant} par Rs {amt_n} ke liye use hua. Agar aap nahi the to app se block karein.",
        ],
        "hi": [
            "आपके खाते {acct} से {date} को ₹{amt_n} डेबिट हुए। आपने नहीं किया? {tollfree} पर कॉल करें। -{bank_short}",
            "आपके खाते {acct} में ₹{amt_n} जमा हुए। उपलब्ध शेष ₹{bal}। -{bank_short}",
            "UPI से ₹{amt_n} {name} को भेजे गए। संदर्भ {ref}।",
        ],
        "ta": [
            "உங்கள் கணக்கு {acct} இலிருந்து {date} அன்று ₹{amt_n} பற்று வைக்கப்பட்டது. நீங்கள் செய்யவில்லையா? {tollfree} அழைக்கவும்.",
            "உங்கள் கணக்கில் ₹{amt_n} வரவு வைக்கப்பட்டது. இருப்பு ₹{bal}. -{bank_short}",
        ],
    },
    "BANK_OTP": {
        "en": [
            "{otp} is your OTP for txn of Rs {amt_n} at {merchant}. Valid for 10 mins. Do not share this OTP with anyone. -{bank_short}",
            "Your {brand} verification code is {otp}. Do not share it with anyone, {brand} will never call you to ask for it.",
            "OTP for login to {bank} NetBanking is {otp}. Never share your OTP, PIN or password. The bank never asks for these.",
            "{otp} is the One Time Password to register UPI on this device. Don't share it with anyone, not even bank staff.",
            "Use OTP {otp} to complete your {brand} order delivery. Please do not share it with anyone except the delivery agent at your door.",
            "Dear Customer, {otp} is your OTP to set UPI PIN. It is valid for 5 minutes. DO NOT share this with anyone. -{bank_short}",
            "{otp} is your VTOP login OTP. Do not disclose it to anyone. - VIT",
            "Your OTP to change your mobile number is {otp}. If you did not request this, call {tollfree}. Never share OTP.",
        ],
        "hinglish": [
            "{otp} aapka OTP hai Rs {amt_n} ke txn ke liye. Kisi ke saath share na karein. -{bank_short}",
            "Aapka login OTP {otp} hai. Bank kabhi OTP nahi maangta, share na kare.",
            "{brand} OTP: {otp}. Ye code kisi ko na bataye.",
            "UPI PIN set karne ka OTP {otp} hai. 5 min valid. Share mat karo.",
        ],
        "hi": [
            "{otp} आपका ओटीपी है ₹{amt_n} के लेनदेन के लिए। इसे किसी के साथ साझा न करें। -{bank_short}",
            "आपका लॉगिन ओटीपी {otp} है। बैंक कभी ओटीपी नहीं मांगता, किसी को न बताएं।",
            "{brand} सत्यापन कोड {otp} है। इसे किसी के साथ साझा न करें।",
        ],
        "ta": [
            "{otp} என்பது ₹{amt_n} பரிவர்த்தனைக்கான உங்கள் OTP. இதை யாருடனும் பகிர வேண்டாம். -{bank_short}",
            "உங்கள் உள்நுழைவு ஓடிபி {otp}. வங்கி ஒருபோதும் கேட்காது, பகிர வேண்டாம்.",
        ],
    },
    "MERCHANT_RECEIPT": {
        "en": [
            "Thank you for shopping at {merchant}. Paid Rs {amt_n} via UPI. Order #{order}. Invoice: https://www.{merchant_domain}/invoice",
            "Payment of Rs {amt_n} to {merchant} successful. UPI Ref {ref}. Rate your experience in the app.",
            "{merchant}: We received your payment of ₹{amt_n} for order {order}. Track it at https://www.{merchant_domain}/orders",
            "Your {merchant} bill of Rs {amt_n} is paid. Earn 2% cashback on your next order with {upi_app}.",
            "Receipt: ₹{amt_n} paid to VIT Food Court on {date} at {time}. Enjoy your meal!",
            "Recharge successful! Rs {amt_n} for {mobile_op} prepaid. Validity 28 days. Txn ID {ref}.",
            "Your IRCTC booking is confirmed. PNR {pnr}. Amount paid Rs {amt_n}. Visit https://www.irctc.co.in for details.",
            "Paid ₹{amt_n} to {name} (Auto). Thank you for using {upi_app}.",
        ],
        "hinglish": [
            "{merchant} pe Rs {amt_n} ka payment ho gaya. Order #{order}. Dhanyavaad!",
            "Aapka {mobile_op} recharge Rs {amt_n} successful raha. Validity 28 din.",
            "Rs {amt_n} canteen ko pay ho gaye. Thank you!",
            "Order confirm ho gaya, Rs {amt_n} mil gaye. Delivery kal tak. - {merchant}",
        ],
        "hi": [
            "{merchant} पर ₹{amt_n} का भुगतान सफल रहा। ऑर्डर #{order}। धन्यवाद!",
            "आपका {mobile_op} रिचार्ज ₹{amt_n} सफल रहा। वैधता 28 दिन।",
            "₹{amt_n} का भुगतान प्राप्त हुआ। आपका ऑर्डर जल्द भेजा जाएगा।",
        ],
        "ta": [
            "{merchant} இல் ₹{amt_n} கட்டணம் வெற்றிகரமாக செலுத்தப்பட்டது. ஆர்டர் #{order}. நன்றி!",
            "உங்கள் {mobile_op} ரீசார்ஜ் ₹{amt_n} வெற்றிகரமாக முடிந்தது.",
        ],
    },
    "AUTOPAY_NOTICE": {
        "en": [
            "Reminder: AutoPay of Rs {amt_n} for {subscription} will be debited from your A/c {acct} on {date}. To cancel, use the {upi_app} app.",
            "UPI AutoPay mandate created for {subscription}, max Rs {amt_n}/month. Manage mandates in your UPI app.",
            "Your {subscription} subscription renews on {date}. Rs {amt_n} will be charged via UPI AutoPay.",
            "Your SIP of Rs {amt_n} in {fund} will be debited on {date} via e-mandate. -{bank_short}",
            "Mandate request from {subscription} for Rs {amt_n} has been approved. You can revoke it any time in {upi_app}.",
            "EMI of Rs {amt_n} for loan {acct} is due on {date}. Please keep sufficient balance. -{bank}",
            "Electricity bill of Rs {amt_n} paid via AutoPay. Thank you. - {eb}",
            "Your insurance premium of Rs {amt_n} will be auto-debited on {date}. Policy {order}.",
        ],
        "hinglish": [
            "Yaad dilana: {subscription} ka autopay Rs {amt_n} {date} ko kata jayega.",
            "Aapka {subscription} mandate ban gaya hai, max Rs {amt_n} mahina. UPI app me manage karein.",
            "Loan EMI Rs {amt_n} {date} ko due hai, khate me balance rakhein. -{bank_short}",
            "Bijli bill Rs {amt_n} autopay se bhar diya gaya. Dhanyavaad. - {eb}",
        ],
        "hi": [
            "याद दिलाना: {subscription} के लिए ₹{amt_n} का ऑटोपे {date} को कटेगा।",
            "आपकी लोन ईएमआई ₹{amt_n} {date} को देय है। खाते में पर्याप्त शेष रखें।",
            "बिजली बिल ₹{amt_n} का भुगतान ऑटोपे से हो गया। धन्यवाद।",
        ],
        "ta": [
            "நினைவூட்டல்: {subscription} க்கான ₹{amt_n} ஆட்டோபே {date} அன்று பற்று வைக்கப்படும்.",
            "உங்கள் கடன் EMI ₹{amt_n} {date} அன்று செலுத்த வேண்டும். போதுமான இருப்பு வைக்கவும்.",
        ],
    },
    "COLLEGE_NOTICE": {
        "en": [
            "Dear Student, the CAT-2 schedule for {course} is published. Check your slot at https://vtop.vit.ac.in",
            "VIT: Fee payment for the Winter Semester opens on {date}. Pay only through VTOP (https://vtop.vit.ac.in). Ignore messages asking for fees elsewhere.",
            "Reminder: {course} lab assessment tomorrow at {time} in SJT-{room}. Carry your ID card.",
            "Hostel notice: water supply will be off in Block {block} on {date} from 10 AM to 1 PM for maintenance.",
            "Your FAT hall ticket is available on VTOP. Download it from https://vtop.vit.ac.in before {date}.",
            "VIT Library: the book you borrowed is due on {date}. Renew it online at https://library.vit.ac.in",
            "Placement update: {brand} pre-placement talk on {date} at Anna Auditorium. Register on https://vtop.vit.ac.in",
            "Dear Student, your attendance in {course} is below 75%. Please meet your faculty advisor this week.",
            "Your VTOP password will expire in 7 days. Change it only at https://vtop.vit.ac.in after logging in.",
        ],
        "hinglish": [
            "CAT-2 ka schedule aa gaya hai, apna slot https://vtop.vit.ac.in pe check karo.",
            "Fee payment sirf VTOP se karein (https://vtop.vit.ac.in), kisi aur link pe nahi.",
            "Kal {time} baje {course} ka lab test hai, ID card le kar aana.",
            "Hostel me kal subah 10 se 1 baje tak paani band rahega.",
        ],
        "hi": [
            "प्रिय छात्र, CAT-2 की समय-सारणी जारी हो गई है। अपना स्लॉट https://vtop.vit.ac.in पर देखें।",
            "फीस का भुगतान केवल VTOP (https://vtop.vit.ac.in) से करें।",
            "कल {time} बजे {course} की लैब परीक्षा है। अपना आईडी कार्ड साथ लाएँ।",
        ],
        "ta": [
            "அன்புள்ள மாணவரே, CAT-2 அட்டவணை வெளியிடப்பட்டது. உங்கள் நேரத்தை https://vtop.vit.ac.in இல் பார்க்கவும்.",
            "கட்டணத்தை VTOP (https://vtop.vit.ac.in) மூலம் மட்டுமே செலுத்தவும்.",
        ],
    },
    "DELIVERY_UPDATE": {
        "en": [
            "Your {brand} order #{order} is out for delivery today. Track: https://www.{brand_domain}/track",
            "{courier}: Shipment {awb} will be delivered by {time}. Delivery agent {name} will call you.",
            "Your package could not be delivered as nobody was home. We will try again tomorrow.",
            "Order #{order} delivered. Rate your delivery experience in the {brand} app.",
            "Your {brand} order has been shipped and will arrive by {date}. Pay on delivery: Rs {amt_n}.",
            "{courier}: Your parcel is at the {city} hub. Expected delivery {date}.",
            "OTP for your {brand} delivery is {otp}. Share it only with the delivery agent at your doorstep.",
            "Your Swiggy order from {restaurant} is on the way! {name} will reach in 12 mins.",
        ],
        "hinglish": [
            "Aapka {brand} order aaj deliver hoga. Track karein: https://www.{brand_domain}/track",
            "Delivery boy {name} 15 min me pahunch jayega, please ghar pe rahein.",
            "Aapka parcel {city} hub pe hai, kal tak aa jayega.",
            "Order deliver ho gaya. {brand} app me rating dein.",
        ],
        "hi": [
            "आपका {brand} ऑर्डर आज डिलीवर होगा। ट्रैक करें: https://www.{brand_domain}/track",
            "आपका पार्सल {city} हब पर है, कल तक पहुँच जाएगा।",
            "डिलीवरी एजेंट {name} 15 मिनट में पहुँचेंगे।",
        ],
        "ta": [
            "உங்கள் {brand} ஆர்டர் இன்று டெலிவரி செய்யப்படும். கண்காணிக்க: https://www.{brand_domain}/track",
            "உங்கள் பார்சல் {city} மையத்தில் உள்ளது, நாளை வந்து சேரும்.",
        ],
    },
    "PROMO": {
        "en": [
            "{brand} Big Billion Days: flat 50% off on electronics + 10% instant discount on {bank_short} cards. Shop at https://www.{brand_domain}",
            "Get Rs {amt_small_n} cashback on your first UPI payment with {upi_app}. T&C apply.",
            "Weekend offer at {merchant}: buy 1 get 1 free on all pizzas. Order on the app.",
            "Your {mobile_op} plan expires on {date}. Recharge with Rs 299 for unlimited calls and 2GB/day.",
            "{bank}: Pre-approved personal loan up to Rs 5 lakh at 10.5% p.a. Apply only in the official {bank_short} app.",
            "Diwali sale is live! Up to 70% off on fashion at {brand}. Hurry, ends {date}.",
            "Refer a friend to {upi_app} and both of you get Rs 100 cashback when they make their first payment.",
            "Congratulations, you have earned 250 reward points on your {bank_short} credit card. Redeem them in the app.",
        ],
        "hinglish": [
            "{brand} sale shuru! Electronics pe 50% tak off. App pe shop karein.",
            "Pehle UPI payment pe Rs {amt_small_n} cashback paayein. T&C lagu.",
            "Aapka {mobile_op} plan {date} ko khatam hoga. Rs 299 me recharge karein.",
            "Weekend offer: {merchant} pe 1 ke saath 1 free!",
        ],
        "hi": [
            "{brand} सेल शुरू! इलेक्ट्रॉनिक्स पर 50% तक की छूट। ऐप पर खरीदारी करें।",
            "पहले UPI भुगतान पर ₹{amt_small_n} कैशबैक पाएँ। नियम व शर्तें लागू।",
            "आपका {mobile_op} प्लान {date} को समाप्त होगा। ₹299 में रिचार्ज करें।",
        ],
        "ta": [
            "{brand} விற்பனை தொடங்கியது! மின்னணு பொருட்களுக்கு 50% வரை தள்ளுபடி.",
            "முதல் UPI கட்டணத்தில் ₹{amt_small_n} கேஷ்பேக் பெறுங்கள். நிபந்தனைகள் பொருந்தும்.",
        ],
    },
    "PERSONAL_CHAT": {
        "en": [
            "Hey, sent you {amt_n} for the movie tickets. Check your GPay.",
            "Bro can you send me 300 for the cab? Will return tomorrow.",
            "Mom, I paid the hostel mess fee of {amt_n}. Will call you tonight.",
            "Splitting dinner: your share is {amt_n}. Pay me on {upi_app} whenever you are free.",
            "Did you get the {amt_n} I sent for the trip? Let me know.",
            "Papa please send {amt_n} for the books this week, sending you the list.",
            "I will pay you back the {amt_n} on Friday, got my stipend today.",
            "Can you lend me 500 till Monday? Urgent, my card is not working.",
        ],
        "hinglish": [
            "Bhai pizza ke {amt_n} bhej diye, check kar le.",
            "Yaar 500 bhej de na, kal wapas kar dunga.",
            "Mummy mess fee {amt_n} bhar di hai, raat ko call karta hoon.",
            "Trip ke paise {amt_n} GPay kar diye, mil gaye?",
        ],
        "hi": [
            "भाई, पिज़्ज़ा के {amt_n} भेज दिए हैं, देख लेना।",
            "माँ, मेस फीस भर दी है, रात को फोन करूँगा।",
            "यार, 500 भेज दो, कल लौटा दूँगा।",
        ],
        "ta": [
            "டேய், சினிமா டிக்கெட்டுக்கு {amt_n} அனுப்பிட்டேன், பார்த்துக்கோ.",
            "அம்மா, ஹாஸ்டல் கட்டணம் கட்டிவிட்டேன், இரவு அழைக்கிறேன்.",
        ],
    },
    "CASUAL_CHAT": {
        "en": [
            "Reached home safely. Will call you after dinner.",
            "Are we still meeting at the library at {time}?",
            "Happy birthday {name}! Have an amazing year ahead.",
            "Can you send me the notes for {course}? I missed today's class.",
            "Running 10 mins late, start without me.",
            "Did you watch the match last night? What a finish!",
            "Mom says dinner is ready, come down.",
            "Good morning! Carry an umbrella, it is raining in {city} today.",
            "Thanks for helping me move today, really appreciate it.",
            "Lab got cancelled, see you at the canteen instead?",
            "Send me your address, I will drop the book tomorrow.",
            "Ok, I will check and tell you by evening.",
            "Congratulations on clearing the exam, so proud of you!",
            "Can you call me when you are free? Need to ask something about the project.",
            "The movie was boring honestly, I slept halfway through.",
            "Merry Christmas to you and the whole family!",
            "Wifi is down in our block again, so annoying.",
            "Bring your charger, mine is dead.",
        ],
        "hinglish": [
            "Ghar pahunch gaya, raat ko call karta hoon.",
            "Kal library chalein? {time} baje milte hain.",
            "Happy birthday bhai! Party kab de raha hai?",
            "Yaar notes bhej de na, aaj class miss ho gayi.",
            "Thoda late ho jayega, tum log shuru karo.",
            "Match dekha kal? Kya finish tha!",
            "Mummy bol rahi hai khana ready hai, neeche aa jao.",
            "Theek hai, sham tak bata dunga.",
            "Charger le aana, mera dead hai.",
            "Abhi free hoon, call kar lo jab time mile.",
        ],
        "hi": [
            "घर पहुँच गया हूँ, रात को फोन करूँगा।",
            "जन्मदिन की बहुत बहुत शुभकामनाएँ! खूब खुश रहो।",
            "कल लाइब्रेरी में मिलते हैं, {time} बजे।",
            "ठीक है, शाम तक बता दूँगा।",
            "माँ कह रही हैं खाना तैयार है।",
            "बधाई हो, परीक्षा में अच्छे नंबर आए!",
        ],
        "ta": [
            "வீட்டுக்கு வந்துட்டேன், இரவு அழைக்கிறேன்.",
            "பிறந்தநாள் வாழ்த்துக்கள்! இனிய நாளாக அமையட்டும்.",
            "நாளை நூலகத்தில் {time}க்கு சந்திப்போம்.",
            "சரி, மாலைக்குள் சொல்கிறேன்.",
            "அம்மா சாப்பாடு ரெடி என்கிறார்.",
        ],
    },
}

OPENERS: dict[str, list[str]] = {
    "en": ["", "Hello, ", "Hi, ", "Dear user, ", "ALERT: ", "Attention: "],
    "hinglish": ["", "Namaste, ", "Hello ji, ", "Sir/Madam, "],
    "hi": ["", "नमस्ते, ", "सूचना: "],
    "ta": ["", "வணக்கம், ", "அறிவிப்பு: "],
}
CLOSERS: dict[str, list[str]] = {
    "en": ["", " Thank you.", " Regards.", " Have a nice day."],
    "hinglish": ["", " Dhanyavaad.", " Thanks ji."],
    "hi": ["", " धन्यवाद।"],
    "ta": ["", " நன்றி."],
}
SALUTATION_PREFIXES = ("dear", "hi", "hey", "hello", "sir", "madam", "mom", "papa", "uncle", "didi", "bro", "bhai")
