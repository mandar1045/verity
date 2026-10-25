import type { MessageAnalysis, QuizItem } from "@contracts/types";
import { CheckCircle2, Loader2, MessageCircle, MessageSquareText, XCircle } from "lucide-react";
import { RiskBadge } from "./RiskBadge";

interface Props {
  item: QuizItem;
  answer: boolean | null;
  analysis: MessageAnalysis | null;
  loading: boolean;
  onAnswer: (saysScam: boolean) => void;
}

export function QuizCard({ item, answer, analysis, loading, onAnswer }: Props) {
  const answered = answer !== null;
  const correct = answered && answer === item.is_scam;
  const Channel = item.channel === "whatsapp" ? MessageCircle : MessageSquareText;
  const top = analysis?.signals.find((s) => s.code !== "MODEL_TEXT") ?? analysis?.signals[0];

  return (
    <div className="card overflow-hidden">
      <div className="bg-surface-2 px-5 py-6 sm:px-8">
        <p className="mb-3 flex items-center gap-1.5 text-xs font-medium text-ink-3">
          <Channel className="h-3.5 w-3.5" aria-hidden />
          {item.channel === "whatsapp" ? "WhatsApp" : "SMS"} from <span className="font-mono text-ink-2">{item.sender}</span>
        </p>
        <div className="max-w-md rounded-2xl rounded-tl-sm border border-line bg-white px-4 py-3 text-[15px] leading-relaxed text-ink shadow-card">
          {item.text}
        </div>
      </div>
      <div className="px-5 py-5 sm:px-8">
        {!answered ? (
          <>
            <p className="mb-3 text-sm font-medium text-ink-2">Would you trust this message?</p>
            <div className="grid grid-cols-2 gap-3">
              <button type="button" className="btn-secondary py-3 text-[15px]" onClick={() => onAnswer(false)}>
                Looks safe
              </button>
              <button type="button" className="btn-secondary py-3 text-[15px]" onClick={() => onAnswer(true)}>
                It’s a scam
              </button>
            </div>
          </>
        ) : (
          <div aria-live="polite">
            <p className={`flex items-center gap-2 text-base font-semibold ${correct ? "text-safe-700" : "text-danger-700"}`}>
              {correct ? <CheckCircle2 className="h-5 w-5" aria-hidden /> : <XCircle className="h-5 w-5" aria-hidden />}
              {correct ? "Correct." : "Not quite."} This message is {item.is_scam ? "a scam" : "genuine"}.
            </p>
            {loading && (
              <p className="mt-3 flex items-center gap-2 text-sm text-ink-3">
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> Asking Verity why…
              </p>
            )}
            {analysis && (
              <div className="mt-3 space-y-3 rounded-lg border border-line bg-surface-2 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-medium text-ink-3">Verity says</span>
                  <RiskBadge label={analysis.label} score={analysis.risk_score} />
                </div>
                {top && item.is_scam && (
                  <p className="text-sm text-ink-2">
                    <span className="font-semibold text-ink">The giveaway: {top.title}.</span> {top.description}
                  </p>
                )}
                <p className="text-sm leading-relaxed text-ink-2">{analysis.explanation}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
