import type { Label } from "@contracts/types";
import { AlertOctagon, AlertTriangle, ShieldCheck, type LucideIcon } from "lucide-react";

export interface RiskMeta {
  icon: LucideIcon;
  text: string; // text colour class
  bg: string; // tinted background class
  border: string;
  fill: string; // hex for SVG marks
  track: string; // lighter step of the same ramp
}

// Every risk state is colour + icon + text; colour never carries meaning alone.
export const RISK: Record<Label, RiskMeta> = {
  SAFE: { icon: ShieldCheck, text: "text-safe-700", bg: "bg-safe-50", border: "border-safe-300", fill: "#1f8a46", track: "#d3eedb" },
  SUSPICIOUS: { icon: AlertTriangle, text: "text-warn-700", bg: "bg-warn-50", border: "border-warn-300", fill: "#d08a00", track: "#feecc2" },
  HIGH_RISK: { icon: AlertOctagon, text: "text-danger-700", bg: "bg-danger-50", border: "border-danger-300", fill: "#cc3a2e", track: "#fbd9d5" },
};

// Categorical slots for highlighting individual signals (fixed order, never cycled).
// Validated default palette: blue, orange, aqua, yellow, magenta, green, violet, red.
export const SIGNAL_SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];
