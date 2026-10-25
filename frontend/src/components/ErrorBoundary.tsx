import { Component, type ErrorInfo, type ReactNode } from "react";

interface State {
  failed: boolean;
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Verity UI error", error, info.componentStack);
  }

  render(): ReactNode {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="mx-auto mt-24 max-w-md px-4 text-center">
        <h1 className="font-serif text-2xl font-semibold">Something went wrong on this screen.</h1>
        <p className="mt-2 text-sm text-ink-3">Your data is safe. Reload to try again.</p>
        <button type="button" className="btn-primary mt-6" onClick={() => window.location.reload()}>
          Reload Verity
        </button>
      </div>
    );
  }
}
