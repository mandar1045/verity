import { AlertOctagon, MessageCircle } from "lucide-react";

const mark = (color: string) => ({ backgroundColor: `${color}26`, boxShadow: `inset 0 -2px 0 ${color}` });

/** A static, illustrative preview of a real analysis (the Hinglish refund sample). */
export function HeroPreview() {
  return (
    <div className="relative mx-auto w-full max-w-md" aria-hidden>
      <div className="absolute -inset-4 -z-10 rounded-[28px] bg-gradient-to-br from-brand-50 via-white to-danger-50" />
      <div className="rounded-2xl border border-line bg-surface p-4 shadow-pop sm:p-5">
        <div className="flex items-center gap-2 text-xs font-medium text-ink-3">
          <MessageCircle className="h-3.5 w-3.5" /> WhatsApp · +91 98765 43210
        </div>
        <p className="mt-2 rounded-2xl rounded-tl-sm bg-surface-3 px-3.5 py-2.5 text-[14px] leading-[1.8] text-ink">
          Aapka refund Rs 2499 approve ho gaya hai.{" "}
          <span className="rounded-[3px] px-0.5" style={mark("#2a78d6")}>
            Collect request accept karke PIN daalo
          </span>
          , paise{" "}
          <span className="rounded-[3px] px-0.5" style={mark("#eb6834")}>
            turant
          </span>{" "}
          milenge.
        </p>
        <div className="mt-4 flex items-center gap-4 rounded-xl border border-danger-100 bg-danger-50 p-3.5">
          <div className="flex h-14 w-14 shrink-0 flex-col items-center justify-center rounded-full border-[5px] border-danger-600 bg-white">
            <span className="text-lg font-semibold leading-none text-ink">98</span>
          </div>
          <div>
            <p className="flex items-center gap-1.5 text-sm font-semibold text-danger-700">
              <AlertOctagon className="h-4 w-4" /> High risk · Fake refund
            </p>
            <p className="mt-0.5 text-[13px] leading-snug text-ink-2">You never need a PIN to receive money. A PIN only sends money out.</p>
          </div>
        </div>
        <div className="mt-3 rounded-xl border border-line bg-surface-2 p-3">
          <div className="flex gap-1.5 text-[11px] font-semibold">
            <span className="rounded-md px-2 py-0.5 text-ink-3">EN</span>
            <span className="rounded-md bg-white px-2 py-0.5 text-brand-800 shadow-card ring-1 ring-line">हिं</span>
            <span className="rounded-md px-2 py-0.5 text-ink-3">தமிழ்</span>
          </div>
          <p className="mt-2 text-[13px] leading-snug text-ink-2">पैसे पाने के लिए PIN की कभी ज़रूरत नहीं होती। PIN से हमेशा पैसे बाहर जाते हैं।</p>
        </div>
      </div>
    </div>
  );
}
