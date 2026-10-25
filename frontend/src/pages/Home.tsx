import { ArrowRight, Check, HandCoins, Languages, PauseOctagon, type LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { HeroPreview } from "../components/home/HeroPreview";
import { Pipeline } from "../components/home/Pipeline";
import { useAsync } from "../hooks/useAsync";

const IDEAS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: HandCoins,
    title: "The PIN-to-receive rule",
    body: "You never need a UPI PIN to receive money. Verity treats any request to enter a PIN “to receive” a refund or payment as its strongest scam signal.",
  },
  {
    icon: Languages,
    title: "Explains, in your language",
    body: "Every warning points at the exact words that gave the scam away and says what to do next, in English, हिन्दी or தமிழ்.",
  },
  {
    icon: PauseOctagon,
    title: "Pause before you pay",
    body: "On a risky collect request, Verity interrupts at the moment of payment, not after the money is gone. Declining takes one tap; trusting takes two.",
  },
];

const PRINCIPLES = [
  "Never opens or fetches links",
  "Stores no message text",
  "Works offline, with no API key",
  "Advises; never blocks a payment",
  "100% synthetic data",
];

const SDGS = [
  ["SDG 8.10", "Access to financial services"],
  ["SDG 10", "First-time and non-English users"],
  ["SDG 16", "Reducing financial crime"],
  ["SDG 4", "Digital-safety awareness"],
];

function Evidence() {
  const { data } = useAsync(() => api.metrics(), []);
  const fused = data?.message.models.find((m) => m.key === "fused");
  const txn = data?.transaction?.models.find((m) => m.key === "gbm_floors");
  const items = [
    [fused ? fused.f1.toFixed(3) : "—", "Message F1 on unseen templates"],
    [fused ? `${(fused.recall * 100).toFixed(1)}%` : "—", "of scams caught"],
    [txn ? txn.f1.toFixed(3) : "—", "Transaction F1 on the last 15 days"],
    [txn ? txn.false_alarms_per_1000.toFixed(1) : "—", "false alarms per 1,000 payments"],
  ];
  return (
    <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line lg:grid-cols-4">
      {items.map(([value, label]) => (
        <div key={label} className="bg-surface p-5">
          <p className="text-3xl font-semibold tracking-tight text-ink">{value}</p>
          <p className="mt-1 text-[13px] text-ink-3">{label}</p>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  return (
    <div className="space-y-20">
      <section className="grid items-center gap-12 pt-2 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)]">
        <div>
          <p className="eyebrow mb-4 text-brand-700">Scam check for students and first-time UPI users</p>
          <h1 className="font-serif text-[2.4rem] font-semibold leading-[1.08] tracking-tight sm:text-[3.4rem]">
            Most fraud tools flag. Verity explains, in your language, before you hit Pay.
          </h1>
          <p className="mt-5 max-w-xl text-[17px] leading-relaxed text-ink-2">
            Paste a suspicious SMS, WhatsApp message or email, or watch a payment feed. Verity shows the exact warning signs, explains
            them in English, Hindi or Tamil, and stops you at the moment that matters.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/check" className="btn-primary px-5 py-3 text-[15px]">
              Check a message <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
            <Link to="/transactions?user=U003" className="btn-secondary px-5 py-3 text-[15px]">
              See a demo account
            </Link>
          </div>
          <ul className="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-[13px] text-ink-3">
            {PRINCIPLES.slice(0, 3).map((p) => (
              <li key={p} className="flex items-center gap-1.5">
                <Check className="h-4 w-4 text-safe-600" aria-hidden /> {p}
              </li>
            ))}
          </ul>
        </div>
        <HeroPreview />
      </section>

      <section aria-labelledby="ideas">
        <h2 id="ideas" className="font-serif text-3xl font-semibold tracking-tight">Three ideas, working together</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {IDEAS.map((idea) => (
            <article key={idea.title} className="card card-pad">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700 text-white">
                <idea.icon className="h-5 w-5" aria-hidden />
              </span>
              <h3 className="mt-4 text-lg font-semibold">{idea.title}</h3>
              <p className="mt-2 text-[15px] leading-relaxed text-ink-3">{idea.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section aria-labelledby="how">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
          <h2 id="how" className="font-serif text-3xl font-semibold tracking-tight">How it works</h2>
          <p className="text-sm text-ink-3">Deterministic and auditable. The verdict never depends on an LLM.</p>
        </div>
        <Pipeline />
      </section>

      <section aria-labelledby="evidence" className="space-y-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h2 id="evidence" className="font-serif text-3xl font-semibold tracking-tight">Measured, not claimed</h2>
          <Link to="/report" className="text-sm font-semibold text-brand-700 hover:text-brand-900">
            Read the full model report →
          </Link>
        </div>
        <Evidence />
        <p className="text-xs text-ink-4">Held-out synthetic data; see the report for baselines, per-language results, the external UCI check and failures.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="card card-pad">
          <p className="eyebrow">Responsible by design</p>
          <ul className="mt-3 space-y-2">
            {PRINCIPLES.map((p) => (
              <li key={p} className="flex items-center gap-2 text-[15px] text-ink-2">
                <Check className="h-4 w-4 shrink-0 text-safe-600" aria-hidden /> {p}
              </li>
            ))}
          </ul>
        </div>
        <div className="card card-pad">
          <p className="eyebrow">Sustainable Development Goals</p>
          <dl className="mt-3 grid grid-cols-2 gap-3">
            {SDGS.map(([k, v]) => (
              <div key={k} className="rounded-lg bg-surface-2 p-3">
                <dt className="text-sm font-semibold text-brand-800">{k}</dt>
                <dd className="mt-0.5 text-[13px] text-ink-3">{v}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>
    </div>
  );
}
