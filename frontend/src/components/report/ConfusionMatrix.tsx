// One-hue sequential scale (light -> dark blue); text flips to white on dark cells.
const STEPS = ["#eef3fa", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95"];

function cellStyle(count: number, rowTotal: number) {
  const share = rowTotal ? count / rowTotal : 0;
  const step = Math.min(STEPS.length - 1, Math.round(share * (STEPS.length - 1)));
  return { background: STEPS[step], color: step >= 4 ? "#ffffff" : "#16181d" };
}

interface Props {
  title: string;
  matrix: [[number, number], [number, number]];
  positive?: string;
}

export function ConfusionMatrix({ title, matrix, positive = "scam" }: Props) {
  const [[tn, fp], [fn, tp]] = matrix;
  const rows: [string, number, number][] = [
    ["Actually safe", tn, fp],
    ["Actually " + positive, fn, tp],
  ];
  return (
    <figure>
      <figcaption className="mb-2 text-[13px] font-medium text-ink-2">{title}</figcaption>
      <table className="num w-full table-fixed border-separate text-center text-[13px]" style={{ borderSpacing: 2 }}>
        <thead>
          <tr className="text-[11px] text-ink-4">
            <th className="w-[38%]" />
            <th scope="col" className="pb-1 font-medium">Predicted safe</th>
            <th scope="col" className="pb-1 font-medium">Predicted {positive}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([name, a, b]) => {
            const total = a + b;
            return (
              <tr key={name}>
                <th scope="row" className="pr-2 text-right text-[11px] font-medium text-ink-4">
                  {name}
                </th>
                {[a, b].map((v, j) => (
                  <td key={j} className="rounded-md px-1 py-3 font-semibold" style={cellStyle(v, total)} title={`${v} of ${total}`}>
                    {v.toLocaleString("en-IN")}
                    <span className="block text-[10.5px] font-medium opacity-80">{total ? `${Math.round((v / total) * 100)}%` : "—"}</span>
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </figure>
  );
}
