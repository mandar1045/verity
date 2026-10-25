import { Info } from "lucide-react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { USE_MOCKS } from "../api/client";
import { LanguageToggle } from "./LanguageToggle";
import { Logo } from "./Logo";

const NAV = [
  { to: "/check", label: "Check a message" },
  { to: "/transactions", label: "Transactions" },
  { to: "/learn", label: "Learn" },
  { to: "/report", label: "Model report" },
];

function NavItems({ compact = false }: { compact?: boolean }) {
  return (
    <>
      {NAV.map((n) => (
        <NavLink
          key={n.to}
          to={n.to}
          className={({ isActive }) =>
            [
              "whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors",
              isActive ? "bg-brand-50 text-brand-800" : "text-ink-2 hover:bg-surface-3 hover:text-ink",
              compact ? "px-2.5 py-1.5 text-[13px]" : "",
            ].join(" ")
          }
        >
          {n.label}
        </NavLink>
      ))}
    </>
  );
}

export function Layout() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pathname]);

  return (
    <div className="flex min-h-screen flex-col">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-50 focus:rounded focus:bg-white focus:px-3 focus:py-2">
        Skip to content
      </a>
      <div className="border-b border-brand-100 bg-brand-50 text-brand-800">
        <p className="mx-auto flex max-w-page items-center justify-center gap-2 px-4 py-1.5 text-center text-xs font-medium">
          <Info className="h-3.5 w-3.5 shrink-0" aria-hidden />
          Prototype — synthetic data, no real UPI connection{USE_MOCKS ? " · offline demo mode" : ""}
        </p>
      </div>
      <header className="sticky top-0 z-30 border-b border-line bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/80">
        <div className="mx-auto flex h-16 max-w-page items-center gap-6 px-4 sm:px-6">
          <NavLink to="/" className="shrink-0 rounded-md" aria-label="Verity home">
            <Logo />
          </NavLink>
          <nav aria-label="Main" className="hidden items-center gap-1 md:flex">
            <NavItems />
          </nav>
          <div className="ml-auto">
            <LanguageToggle />
          </div>
        </div>
        <nav aria-label="Main" className="flex gap-1 overflow-x-auto border-t border-line px-3 py-1.5 md:hidden">
          <NavItems compact />
        </nav>
      </header>
      <main id="main" className="mx-auto w-full max-w-page flex-1 px-4 pb-16 pt-8 sm:px-6 sm:pt-10">
        <Outlet />
      </main>
      <footer className="border-t border-line bg-surface">
        <div className="mx-auto flex max-w-page flex-col gap-2 px-4 py-6 text-xs text-ink-3 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>Verity advises; you decide. It never blocks a payment and never opens links.</p>
          <p>
            Lost money? Call <strong className="text-ink-2">1930</strong> or report at{" "}
            <span className="font-medium text-ink-2">cybercrime.gov.in</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
