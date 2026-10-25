// Evidence offsets from the API are Python string indices (Unicode code points).
// JS strings index UTF-16 code units, so emoji would shift every later span.
// We slice by code points and merge overlapping spans into segments.
import type { Signal } from "@contracts/types";

export interface Segment {
  text: string;
  signals: number[]; // indices into the signal list, strongest first
}

export function segmentText(text: string, signals: Signal[]): Segment[] {
  const chars = Array.from(text);
  const owners: number[][] = chars.map(() => []);
  signals.forEach((s, idx) => {
    for (const e of s.evidence) {
      const start = Math.max(0, e.start);
      const end = Math.min(chars.length, e.end);
      for (let i = start; i < end; i++) {
        if (!owners[i].includes(idx)) owners[i].push(idx);
      }
    }
  });
  const segments: Segment[] = [];
  for (let i = 0; i < chars.length; i++) {
    const last = segments[segments.length - 1];
    if (last && last.signals.join(",") === owners[i].join(",")) {
      last.text += chars[i];
    } else {
      segments.push({ text: chars[i], signals: [...owners[i]] });
    }
  }
  return segments;
}
