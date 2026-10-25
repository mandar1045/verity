import { AlertCircle, RotateCw } from "lucide-react";
import type { ReactNode } from "react";

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-surface-3 ${className}`} aria-hidden />;
}

export function SkeletonCard({ lines = 4 }: { lines?: number }) {
  return (
    <div className="card card-pad space-y-3" role="status" aria-label="Loading">
      <Skeleton className="h-5 w-1/3" />
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} className={`h-4 ${i % 2 ? "w-5/6" : "w-full"}`} />
      ))}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="card card-pad flex flex-col items-start gap-3 border-danger-100 sm:flex-row sm:items-center">
      <AlertCircle className="h-5 w-5 shrink-0 text-danger-600" aria-hidden />
      <div className="flex-1">
        <p className="font-medium text-ink">We couldn’t load this.</p>
        <p className="text-sm text-ink-3">{message} Is the backend running on port 8000?</p>
      </div>
      {onRetry && (
        <button type="button" className="btn-secondary" onClick={onRetry}>
          <RotateCw className="h-4 w-4" aria-hidden /> Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ icon, title, children }: { icon: ReactNode; title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-line-strong bg-surface-2 px-6 py-14 text-center">
      <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-700">{icon}</div>
      <p className="font-medium text-ink">{title}</p>
      {children && <div className="mt-1 max-w-sm text-sm text-ink-3">{children}</div>}
    </div>
  );
}

export function SectionTitle({ children, aside }: { children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-3 flex items-baseline justify-between gap-3">
      <h3 className="text-sm font-semibold text-ink">{children}</h3>
      {aside && <div className="text-xs text-ink-3">{aside}</div>}
    </div>
  );
}

export function PageHeader({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return (
    <header className="mb-8 max-w-3xl">
      <p className="eyebrow mb-2">{eyebrow}</p>
      <h1 className="font-serif text-3xl font-semibold leading-tight tracking-tight sm:text-[2.5rem]">{title}</h1>
      {children && <div className="mt-3 text-[15px] leading-relaxed text-ink-2 sm:text-base">{children}</div>}
    </header>
  );
}
