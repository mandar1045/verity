import type { BreakdownRow } from "@contracts/types";
import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Props {
  rows: BreakdownRow[];
  metric: string;
  nameOf?: (group: string) => string;
}

const BAR = 14;
const ROW = 34;

function TooltipBody({ active, payload, metric }: { active?: boolean; payload?: { payload: BreakdownRow & { name: string } }[]; metric: string }) {
  if (!active || !payload?.length) return null;
  const r = payload[0].payload;
  return (
    <div className="rounded-lg border border-line bg-white px-3 py-2 text-xs shadow-pop">
      <p className="num text-sm font-semibold text-ink">{(r.value * 100).toFixed(1)}%</p>
      <p className="text-ink-3">
        {metric} · {r.name} · n = {r.n}
      </p>
    </div>
  );
}

/** Single-series horizontal bars (one colour, no legend), value at the tip, 0–100% axis. */
export function BreakdownBars({ rows, metric, nameOf = (g) => g }: Props) {
  const data = [...rows].sort((a, b) => b.value - a.value).map((r) => ({ ...r, name: nameOf(r.group) }));
  return (
    <div style={{ height: data.length * ROW + 36 }} role="img" aria-label={`${metric} by group`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 52, bottom: 4, left: 4 }} barCategoryGap={ROW - BAR}>
          <CartesianGrid horizontal={false} stroke="#ebe9e3" />
          <XAxis
            type="number"
            domain={[0, 1]}
            ticks={[0, 0.25, 0.5, 0.75, 1]}
            tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
            tick={{ fontSize: 11, fill: "#7a808c" }}
            axisLine={{ stroke: "#d3d0c6" }}
            tickLine={false}
          />
          <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 12, fill: "#424854" }} axisLine={false} tickLine={false} />
          <Tooltip cursor={{ fill: "#f2f1ec" }} content={<TooltipBody metric={metric} />} />
          <Bar dataKey="value" fill="#2c5ea8" barSize={BAR} radius={[0, 4, 4, 0]} isAnimationActive={false}>
            <LabelList dataKey="value" position="right" formatter={(v: number) => `${(v * 100).toFixed(1)}%`} style={{ fontSize: 11, fill: "#424854", fontWeight: 600 }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
