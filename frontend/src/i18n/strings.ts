// UI strings for the parts of the screen that change with the language toggle.
// Analysis text itself (explanations, steps, signal titles) comes translated from the API.
// Hindi and Tamil are machine-drafted and need native review.
import type { Lang } from "@contracts/types";

const en = {
  SAFE: "Looks safe",
  SUSPICIOUS: "Suspicious",
  HIGH_RISK: "High risk",
  riskScore: "Risk score",
  why: "Why we think so",
  whatToDo: "What to do now",
  signalsFound: "Warning signs found",
  noSignals: "No warning signs found.",
  yourMessage: "Your message, with the warning signs marked",
  linksInMessage: "Links in this message",
  linksNote: "Links are shown as text only. Verity never opens them.",
  wasWrong: "Was this wrong?",
  thanks: "Thanks, noted for review.",
  pauseTitle: "Pause before you pay",
  pauseBody: "This request matches known fraud patterns. Approving it sends money out of your account.",
  decline: "Decline request",
  trust: "I trust this payee",
  confirmTrust: "Tap again to confirm",
  topReasons: "Top reasons",
  scamType: "Looks like",
} as const;

export type UiKey = keyof typeof en;

const hi: Record<UiKey, string> = {
  SAFE: "सुरक्षित लगता है",
  SUSPICIOUS: "संदिग्ध",
  HIGH_RISK: "उच्च जोखिम",
  riskScore: "जोखिम स्कोर",
  why: "हम ऐसा क्यों मानते हैं",
  whatToDo: "अब क्या करें",
  signalsFound: "मिले खतरे के संकेत",
  noSignals: "कोई खतरे का संकेत नहीं मिला।",
  yourMessage: "आपका संदेश, खतरे के संकेत चिह्नित",
  linksInMessage: "इस संदेश के लिंक",
  linksNote: "लिंक केवल टेक्स्ट के रूप में दिखाए गए हैं। Verity इन्हें कभी नहीं खोलता।",
  wasWrong: "क्या यह गलत था?",
  thanks: "धन्यवाद, समीक्षा के लिए दर्ज किया गया।",
  pauseTitle: "भुगतान से पहले रुकें",
  pauseBody: "यह अनुरोध जाने-पहचाने धोखाधड़ी के तरीकों से मेल खाता है। मंज़ूर करने पर आपके खाते से पैसे जाएँगे।",
  decline: "अनुरोध अस्वीकार करें",
  trust: "मुझे इस प्राप्तकर्ता पर भरोसा है",
  confirmTrust: "पक्का करने के लिए फिर से दबाएँ",
  topReasons: "मुख्य कारण",
  scamType: "यह लगता है",
};

const ta: Record<UiKey, string> = {
  SAFE: "பாதுகாப்பாகத் தெரிகிறது",
  SUSPICIOUS: "சந்தேகத்திற்குரியது",
  HIGH_RISK: "அதிக ஆபத்து",
  riskScore: "ஆபத்து மதிப்பெண்",
  why: "ஏன் இப்படி நினைக்கிறோம்",
  whatToDo: "இப்போது என்ன செய்ய வேண்டும்",
  signalsFound: "கண்டறிந்த எச்சரிக்கை அறிகுறிகள்",
  noSignals: "எச்சரிக்கை அறிகுறிகள் இல்லை.",
  yourMessage: "உங்கள் செய்தி, எச்சரிக்கை அறிகுறிகள் குறிக்கப்பட்டுள்ளன",
  linksInMessage: "இந்தச் செய்தியில் உள்ள இணைப்புகள்",
  linksNote: "இணைப்புகள் உரையாக மட்டுமே காட்டப்படும். Verity அவற்றை ஒருபோதும் திறக்காது.",
  wasWrong: "இது தவறா?",
  thanks: "நன்றி, மதிப்பாய்வுக்கு பதிவு செய்யப்பட்டது.",
  pauseTitle: "செலுத்தும் முன் நிறுத்துங்கள்",
  pauseBody: "இந்தக் கோரிக்கை அறியப்பட்ட மோசடி முறைகளுடன் பொருந்துகிறது. ஏற்றால் உங்கள் கணக்கிலிருந்து பணம் போகும்.",
  decline: "கோரிக்கையை நிராகரிக்கவும்",
  trust: "இந்தப் பெறுநரை நம்புகிறேன்",
  confirmTrust: "உறுதிப்படுத்த மீண்டும் தட்டவும்",
  topReasons: "முக்கிய காரணங்கள்",
  scamType: "இது போலத் தெரிகிறது",
};

export const UI: Record<Lang, Record<UiKey, string>> = { en, hi, ta };

export const LANG_OPTIONS: { value: Lang; short: string; name: string }[] = [
  { value: "en", short: "EN", name: "English" },
  { value: "hi", short: "हिं", name: "हिन्दी" },
  { value: "ta", short: "தமிழ்", name: "தமிழ்" },
];
