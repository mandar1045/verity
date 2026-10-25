export function LogoMark({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <rect width="32" height="32" rx="8" fill="#1a4480" />
      <path d="M16 6.5 8.5 9.4v6.1c0 4.6 3.1 8.6 7.5 10 4.4-1.4 7.5-5.4 7.5-10V9.4L16 6.5Z" fill="none" stroke="#fff" strokeWidth="2" strokeLinejoin="round" />
      <path d="m12.4 16.1 2.5 2.5 4.8-5" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Logo() {
  return (
    <span className="flex items-center gap-2.5">
      <LogoMark />
      <span className="font-serif text-[22px] font-semibold leading-none tracking-tight text-ink">Verity</span>
    </span>
  );
}
