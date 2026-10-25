import type { FeedbackKind, Label } from "@contracts/types";
import { Check, Flag } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import { useLang } from "../i18n/LangContext";

const LABELS: Label[] = ["SAFE", "SUSPICIOUS", "HIGH_RISK"];

/** "Was this wrong?" Stores only the analysis id and the corrected label. */
export function FeedbackButton({ analysisId, kind, current }: { analysisId: string; kind: FeedbackKind; current: Label }) {
  const { t } = useLang();
  const [open, setOpen] = useState(false);
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  async function send(label: Label) {
    setBusy(true);
    try {
      await api.feedback({ analysis_id: analysisId, kind, correct_label: label, note: null });
      setDone(true);
    } finally {
      setBusy(false);
    }
  }

  if (done)
    return (
      <p className="inline-flex items-center gap-1.5 text-sm text-safe-700" role="status">
        <Check className="h-4 w-4" aria-hidden /> {t("thanks")}
      </p>
    );
  if (!open)
    return (
      <button type="button" className="btn-ghost -ml-2 px-2 py-1.5 text-[13px]" onClick={() => setOpen(true)}>
        <Flag className="h-4 w-4" aria-hidden /> {t("wasWrong")}
      </button>
    );
  return (
    <div className="flex flex-wrap items-center gap-2" role="group" aria-label="What should the label be?">
      <span className="text-[13px] text-ink-3">It should be:</span>
      {LABELS.filter((l) => l !== current).map((l) => (
        <button key={l} type="button" disabled={busy} className="chip" onClick={() => send(l)}>
          {t(l)}
        </button>
      ))}
    </div>
  );
}
