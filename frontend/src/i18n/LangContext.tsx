import type { Lang } from "@contracts/types";
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { UI, type UiKey } from "./strings";

interface LangState {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: UiKey) => string;
}

const STORAGE_KEY = "verity.lang";
const LangContext = createContext<LangState | null>(null);

function initialLang(): Lang {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved === "en" || saved === "hi" || saved === "ta") return saved;
  } catch {
    /* storage unavailable (private mode): fall back to English */
  }
  return "en";
}

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initialLang);

  useEffect(() => {
    document.documentElement.lang = lang;
    try {
      window.localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      /* ignore */
    }
  }, [lang]);

  const value = useMemo<LangState>(
    () => ({ lang, setLang: setLangState, t: (key) => UI[lang][key] ?? UI.en[key] }),
    [lang],
  );
  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export function useLang(): LangState {
  const ctx = useContext(LangContext);
  if (!ctx) throw new Error("useLang must be used inside LangProvider");
  return ctx;
}
