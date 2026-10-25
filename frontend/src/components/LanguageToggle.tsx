import { Languages } from "lucide-react";
import { useLang } from "../i18n/LangContext";
import { LANG_OPTIONS } from "../i18n/strings";

export function LanguageToggle() {
  const { lang, setLang } = useLang();
  return (
    <div role="radiogroup" aria-label="Explanation language" className="flex items-center gap-1.5">
      <Languages className="hidden h-4 w-4 text-ink-3 sm:block" aria-hidden />
      <div className="flex rounded-lg border border-line-strong bg-surface-2 p-0.5">
        {LANG_OPTIONS.map((o) => {
          const active = o.value === lang;
          return (
            <button
              key={o.value}
              type="button"
              role="radio"
              aria-checked={active}
              aria-label={o.name}
              onClick={() => setLang(o.value)}
              className={[
                "min-w-[2.75rem] rounded-md px-2.5 py-1 text-[13px] font-semibold transition-colors",
                active ? "bg-white text-brand-800 shadow-card ring-1 ring-line" : "text-ink-3 hover:text-ink",
              ].join(" ")}
            >
              {o.short}
            </button>
          );
        })}
      </div>
    </div>
  );
}
