import { StrictMode, lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { Layout } from "./components/Layout";
import { SkeletonCard } from "./components/States";
import { LangProvider } from "./i18n/LangContext";
import Home from "./pages/Home";
import MessageCheck from "./pages/MessageCheck";
import "./index.css";

const TransactionMonitor = lazy(() => import("./pages/TransactionMonitor"));
const Learn = lazy(() => import("./pages/Learn"));
const ModelReport = lazy(() => import("./pages/ModelReport"));

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <LangProvider>
        <BrowserRouter>
          <Suspense fallback={<SkeletonCard lines={8} />}>
            <Routes>
              <Route element={<Layout />}>
                <Route index element={<Home />} />
                <Route path="check" element={<MessageCheck />} />
                <Route path="transactions" element={<TransactionMonitor />} />
                <Route path="learn" element={<Learn />} />
                <Route path="report" element={<ModelReport />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </LangProvider>
    </ErrorBoundary>
  </StrictMode>,
);
