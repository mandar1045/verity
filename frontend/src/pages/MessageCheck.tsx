import type { MessageAnalysis, SampleMessage } from "@contracts/types";
import { ScanSearch } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { MessageForm, type MessageInput } from "../components/MessageForm";
import { MessageResult } from "../components/MessageResult";
import { EmptyState, ErrorState, PageHeader, SkeletonCard } from "../components/States";
import { useAsync } from "../hooks/useAsync";
import { useLang } from "../i18n/LangContext";

export default function MessageCheck() {
  const { lang } = useLang();
  const [params] = useSearchParams();
  const samples = useAsync(() => api.sampleMessages(), []);
  const [input, setInput] = useState<MessageInput>({ text: "", channel: "sms", sender: "" });
  const [analysed, setAnalysed] = useState<MessageInput | null>(null);
  const [result, setResult] = useState<MessageAnalysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  const run = useCallback(
    async (what: MessageInput, scroll: boolean) => {
      setBusy(true);
      setError(null);
      try {
        const res = await api.analyzeMessage({ text: what.text, channel: what.channel, sender: what.sender.trim() || null, lang_out: lang });
        setResult(res);
        setAnalysed(what);
        if (scroll && window.innerWidth < 1024) resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Analysis failed.");
      } finally {
        setBusy(false);
      }
    },
    [lang],
  );

  // Re-request the current analysis when the language changes.
  const lastLang = useRef(lang);
  useEffect(() => {
    if (lastLang.current !== lang && analysed) void run(analysed, false);
    lastLang.current = lang;
  }, [lang, analysed, run]);

  // Deep link: /check?sample=fake-kyc
  const wanted = params.get("sample");
  useEffect(() => {
    const s = samples.data?.find((x) => x.id === wanted);
    if (s) pickSample(s);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [samples.data, wanted]);

  function pickSample(s: SampleMessage) {
    const next = { text: s.text, channel: s.channel, sender: s.sender ?? "" };
    setInput(next);
    void run(next, true);
  }

  return (
    <>
      <PageHeader eyebrow="Message check" title="Is this message a scam?">
        Paste any SMS, WhatsApp message or email. Verity marks exactly which words and links are risky, explains why in
        plain language, and tells you what to do next.
      </PageHeader>
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
        <div className="lg:sticky lg:top-24">
          <MessageForm value={input} onChange={setInput} onSubmit={() => void run(input, true)} busy={busy} samples={samples.error ? [] : samples.data} onSample={pickSample} />
        </div>
        <div ref={resultRef} className="scroll-mt-28">
          {error && <ErrorState message={error} onRetry={() => void run(input, false)} />}
          {!error && result && analysed && <MessageResult result={result} text={analysed.text} stale={busy} />}
          {!error && !result && busy && <SkeletonCard lines={8} />}
          {!error && !result && !busy && (
            <EmptyState icon={<ScanSearch className="h-5 w-5" />} title="Your analysis will appear here">
              Pick an example on the left, or paste a message you received. You get a 0–100 risk score, the exact warning
              signs, and safe next steps.
            </EmptyState>
          )}
        </div>
      </div>
    </>
  );
}
