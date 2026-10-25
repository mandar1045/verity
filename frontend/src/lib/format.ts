import type { Lang } from "@contracts/types";

const inrFmt = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });

export const inr = (n: number): string => `₹${inrFmt.format(n)}`;

export const pct = (x: number, digits = 1): string => `${(x * 100).toFixed(digits)}%`;

export const fixed = (x: number, digits = 3): string => x.toFixed(digits);

export function shortTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit", hour12: false, timeZone: "Asia/Kolkata" });
}

export function humanize(code: string): string {
  return code.toLowerCase().replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

// Mirrors backend i18n scam_type names (hi/ta machine-drafted, need native review).
export const SCAM_TYPE_NAMES: Record<Lang, Record<string, string>> = {
  "en": {
    "COLLECT_REFUND": "Fake refund via collect request",
    "QR_RECEIVE": "QR code 'to receive' trick",
    "FAKE_KYC": "Fake KYC / account block",
    "OTP_THEFT": "OTP theft",
    "REMOTE_ACCESS": "Remote screen-sharing scam",
    "FAKE_CARE": "Fake customer care",
    "TASK_JOB": "Task / part-time job scam",
    "PRIZE": "Fake prize or lottery",
    "WRONG_TRANSFER": "'Sent by mistake' refund trick",
    "BILL_DISCONNECT": "Fake electricity disconnection",
    "VIT_PHISH": "VIT / VTOP phishing",
    "FAMILY_IMPERSONATION": "Family or friend impersonation"
  },
  "hi": {
    "COLLECT_REFUND": "कलेक्ट रिक्वेस्ट से नकली रिफंड",
    "QR_RECEIVE": "'पैसे पाने के लिए QR' धोखा",
    "FAKE_KYC": "नकली KYC / खाता बंद",
    "OTP_THEFT": "OTP चोरी",
    "REMOTE_ACCESS": "स्क्रीन-शेयर धोखा",
    "FAKE_CARE": "नकली कस्टमर केयर",
    "TASK_JOB": "टास्क / पार्ट-टाइम नौकरी धोखा",
    "PRIZE": "नकली इनाम या लॉटरी",
    "WRONG_TRANSFER": "'गलती से भेजा' रिफंड धोखा",
    "BILL_DISCONNECT": "नकली बिजली कटौती",
    "VIT_PHISH": "VIT / VTOP फ़िशिंग",
    "FAMILY_IMPERSONATION": "परिवार या दोस्त बनकर धोखा"
  },
  "ta": {
    "COLLECT_REFUND": "கலெக்ட் கோரிக்கை மூலம் போலி ரீஃபண்ட்",
    "QR_RECEIVE": "'பணம் பெற QR' ஏமாற்று",
    "FAKE_KYC": "போலி KYC / கணக்கு முடக்கம்",
    "OTP_THEFT": "OTP திருட்டு",
    "REMOTE_ACCESS": "திரை பகிர்வு மோசடி",
    "FAKE_CARE": "போலி வாடிக்கையாளர் சேவை",
    "TASK_JOB": "டாஸ்க் / பகுதி நேர வேலை மோசடி",
    "PRIZE": "போலி பரிசு அல்லது லாட்டரி",
    "WRONG_TRANSFER": "'தவறுதலாக அனுப்பினேன்' ஏமாற்று",
    "BILL_DISCONNECT": "போலி மின் துண்டிப்பு",
    "VIT_PHISH": "VIT / VTOP ஃபிஷிங்",
    "FAMILY_IMPERSONATION": "குடும்பம் அல்லது நண்பர் போல நடிப்பு"
  }
};

export const scamTypeName = (code: string | null, lang: Lang = "en"): string | null =>
  code ? (SCAM_TYPE_NAMES[lang][code] ?? SCAM_TYPE_NAMES.en[code] ?? humanize(code)) : null;
