import type { Channel, SampleMessage } from "@contracts/types";
import { Loader2, Mail, MessageCircle, MessageSquareText, ScanSearch } from "lucide-react";
import type { FormEvent } from "react";

export interface MessageInput {
  text: string;
  channel: Channel;
  sender: string;
}

interface Props {
  value: MessageInput;
  onChange: (v: MessageInput) => void;
  onSubmit: () => void;
  busy: boolean;
  samples: SampleMessage[] | null;
  onSample: (s: SampleMessage) => void;
}

const CHANNELS: { value: Channel; label: string; icon: typeof Mail }[] = [
  { value: "sms", label: "SMS", icon: MessageSquareText },
  { value: "whatsapp", label: "WhatsApp", icon: MessageCircle },
  { value: "email", label: "Email", icon: Mail },
];
const MAX = 2000;

export function MessageForm({ value, onChange, onSubmit, busy, samples, onSample }: Props) {
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (value.text.trim()) onSubmit();
  };
  const length = Array.from(value.text).length;
  return (
    <form onSubmit={submit} className="card card-pad space-y-5" aria-label="Check a message">
      <div>
        <label htmlFor="msg" className="label">
          Message you received
        </label>
        <textarea
          id="msg"
          rows={7}
          maxLength={MAX}
          value={value.text}
          onChange={(e) => onChange({ ...value, text: e.target.value })}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit(e);
          }}
          placeholder="Paste an SMS, WhatsApp message or email here…"
          className="field resize-y leading-relaxed"
          aria-describedby="msg-hint"
        />
        <p id="msg-hint" className="mt-1 flex justify-between text-xs text-ink-4">
          <span>English, Hinglish, हिन्दी or தமிழ். Nothing is stored.</span>
          <span className="num">
            {length}/{MAX}
          </span>
        </p>
      </div>

      <div className="grid gap-4">
        <fieldset>
          <legend className="label">Arrived via</legend>
          <div className="flex rounded-lg border border-line-strong bg-surface-2 p-0.5" role="radiogroup">
            {CHANNELS.map(({ value: v, label, icon: Icon }) => (
              <button
                key={v}
                type="button"
                role="radio"
                aria-checked={value.channel === v}
                onClick={() => onChange({ ...value, channel: v })}
                className={[
                  "flex flex-1 items-center justify-center gap-1.5 rounded-md py-1.5 text-[13px] font-medium transition-colors",
                  value.channel === v ? "bg-white text-brand-800 shadow-card ring-1 ring-line" : "text-ink-3 hover:text-ink",
                ].join(" ")}
              >
                <Icon className="h-3.5 w-3.5" aria-hidden />
                {label}
              </button>
            ))}
          </div>
        </fieldset>
        <div>
          <label htmlFor="sender" className="label">
            Sender <span className="font-normal text-ink-4">(optional)</span>
          </label>
          <input
            id="sender"
            value={value.sender}
            onChange={(e) => onChange({ ...value, sender: e.target.value })}
            placeholder={value.channel === "email" ? "name@example.com" : "+91 98765 43210 or VM-SBIINB"}
            className="field py-2"
            autoComplete="off"
          />
        </div>
      </div>

      <button type="submit" className="btn-primary w-full py-3 text-[15px]" disabled={busy || !value.text.trim()}>
        {busy ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : <ScanSearch className="h-4 w-4" aria-hidden />}
        {busy ? "Analysing…" : "Analyse message"}
      </button>

      <div>
        <p className="eyebrow mb-2">Or try a real-style example</p>
        <div className="flex flex-wrap gap-2">
          {samples === null
            ? Array.from({ length: 6 }, (_, i) => <span key={i} className="h-8 w-28 animate-pulse rounded-full bg-surface-3" />)
            : samples.map((s) => (
                <button key={s.id} type="button" className="chip" onClick={() => onSample(s)}>
                  {s.title}
                </button>
              ))}
        </div>
      </div>
    </form>
  );
}
