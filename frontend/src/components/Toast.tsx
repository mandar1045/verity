import { CheckCircle2, Info } from "lucide-react";
import { useEffect } from "react";

export interface ToastMsg {
  id: number;
  tone: "success" | "info";
  text: string;
}

export function Toast({ toast, onDone }: { toast: ToastMsg | null; onDone: () => void }) {
  useEffect(() => {
    if (!toast) return;
    const id = window.setTimeout(onDone, 4500);
    return () => window.clearTimeout(id);
  }, [toast, onDone]);
  if (!toast) return null;
  const Icon = toast.tone === "success" ? CheckCircle2 : Info;
  return (
    <div className="fixed inset-x-0 bottom-5 z-[60] flex justify-center px-4" role="status" aria-live="polite">
      <div className="flex max-w-md items-center gap-2.5 rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink shadow-pop">
        <Icon className={`h-5 w-5 shrink-0 ${toast.tone === "success" ? "text-safe-600" : "text-brand-600"}`} aria-hidden />
        {toast.text}
      </div>
    </div>
  );
}
