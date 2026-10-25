import { ArrowRight, Blend, Brain, FileText, Link2Off, ListChecks, MessageSquareText } from "lucide-react";

const STEPS = [
  { icon: MessageSquareText, title: "Message or payment", body: "SMS, WhatsApp, email, or a simulated UPI transaction." },
  { icon: ListChecks, title: "Rules", body: "22 explainable signals across English, Hinglish, Hindi and Tamil." },
  { icon: Link2Off, title: "Link inspector", body: "Look-alike domains, shorteners, punycode. Links are never opened." },
  { icon: Brain, title: "ML models", body: "TF-IDF + logistic regression for text; gradient boosting + SHAP for payments." },
  { icon: Blend, title: "Score fusion", body: "Weights and thresholds tuned on validation data, plus hard safety floors." },
  { icon: FileText, title: "Plain explanation", body: "Deterministic templates in en/hi/ta. An LLM may only re-phrase." },
];

export function Pipeline() {
  return (
    <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
      {STEPS.map((s, i) => (
        <li key={s.title} className="relative rounded-xl border border-line bg-surface p-4">
          <div className="flex items-center justify-between">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
              <s.icon className="h-[18px] w-[18px]" aria-hidden />
            </span>
            <span className="num text-xs font-semibold text-ink-4">0{i + 1}</span>
          </div>
          <p className="mt-3 text-sm font-semibold text-ink">{s.title}</p>
          <p className="mt-1 text-[13px] leading-snug text-ink-3">{s.body}</p>
          {i < STEPS.length - 1 && (
            <ArrowRight className="absolute -right-[11px] top-1/2 z-10 hidden h-5 w-5 -translate-y-1/2 rounded-full bg-canvas p-0.5 text-ink-4 lg:block" aria-hidden />
          )}
        </li>
      ))}
    </ol>
  );
}
