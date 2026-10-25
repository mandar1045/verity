import type { MessageAnalysis } from "@contracts/types";
import { ArrowRight, RotateCcw, Trophy } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import { QuizCard } from "../components/QuizCard";
import { ErrorState, PageHeader, SkeletonCard } from "../components/States";
import { useAsync } from "../hooks/useAsync";
import { useLang } from "../i18n/LangContext";

const RULES = [
  ["You never need a PIN to receive money.", "A UPI PIN only ever sends money out. Anyone asking for it to “receive” a refund is stealing."],
  ["No bank, college or app will ask for your OTP.", "Real OTP messages always say “do not share”. Asking for one is the scam."],
  ["Verify through the official app, never the message.", "Call the number on your card or open the official app yourself. Links and numbers in the message lead to the scammer."],
];

export default function Learn() {
  const { lang } = useLang();
  const quiz = useAsync(() => api.quiz(), []);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<boolean[]>([]);
  const [analysis, setAnalysis] = useState<MessageAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  const items = quiz.data ?? [];
  const done = items.length > 0 && index >= items.length;
  const item = items[index];
  const score = answers.filter((a, i) => a === items[i]?.is_scam).length;

  async function answer(saysScam: boolean) {
    if (!item) return;
    setAnswers((a) => [...a, saysScam]);
    setLoading(true);
    try {
      setAnalysis(await api.analyzeMessage({ text: item.text, channel: item.channel, sender: item.sender, lang_out: lang }));
    } catch {
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  }
  const next = () => {
    setIndex((i) => i + 1);
    setAnalysis(null);
  };
  const restart = () => {
    setIndex(0);
    setAnswers([]);
    setAnalysis(null);
  };

  return (
    <>
      <PageHeader eyebrow="Learn" title="Can you spot the scam?">
        Five real-style messages. Decide, then see the exact sign that gives each one away.
      </PageHeader>
      <div className="grid items-start gap-8 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)]">
        <div>
          {quiz.error && <ErrorState message={quiz.error} onRetry={quiz.reload} />}
          {!quiz.data && !quiz.error && <SkeletonCard lines={6} />}
          {item && !done && (
            <>
              <div className="mb-3 flex items-center justify-between text-sm">
                <span className="font-medium text-ink-2">
                  Question {index + 1} of {items.length}
                </span>
                <div className="flex gap-1.5" aria-hidden>
                  {items.map((_, i) => (
                    <span key={i} className={`h-1.5 w-8 rounded-full ${i < index ? "bg-brand-700" : i === index ? "bg-brand-300" : "bg-surface-3"}`} />
                  ))}
                </div>
              </div>
              <QuizCard key={item.id} item={item} answer={answers[index] ?? null} analysis={analysis} loading={loading} onAnswer={answer} />
              {answers[index] !== undefined && (
                <button type="button" className="btn-primary mt-4" onClick={next}>
                  {index + 1 < items.length ? "Next message" : "See my score"} <ArrowRight className="h-4 w-4" aria-hidden />
                </button>
              )}
            </>
          )}
          {done && (
            <div className="card card-pad text-center" aria-live="polite">
              <Trophy className="mx-auto h-10 w-10 text-brand-700" aria-hidden />
              <p className="mt-3 font-serif text-4xl font-semibold">
                {score} / {items.length}
              </p>
              <p className="mt-1 text-ink-3">{score === items.length ? "Perfect. You would not fall for these." : "Good practice. Review the three rules and try again."}</p>
              <button type="button" className="btn-secondary mt-5" onClick={restart}>
                <RotateCcw className="h-4 w-4" aria-hidden /> Try again
              </button>
            </div>
          )}
        </div>
        <aside className="card card-pad">
          <p className="eyebrow">Three rules that stop most UPI scams</p>
          <ol className="mt-4 space-y-5">
            {RULES.map(([title, body], i) => (
              <li key={i} className="flex gap-3">
                <span className="num flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-700 text-sm font-semibold text-white">{i + 1}</span>
                <div>
                  <p className="font-semibold leading-snug text-ink">{title}</p>
                  <p className="mt-1 text-sm leading-relaxed text-ink-3">{body}</p>
                </div>
              </li>
            ))}
          </ol>
          <div className="mt-6 rounded-lg bg-brand-50 p-4 text-sm text-brand-900">
            Lost money? Call <strong>1930</strong> immediately or report at <strong>cybercrime.gov.in</strong>. The first hour matters.
          </div>
        </aside>
      </div>
    </>
  );
}
