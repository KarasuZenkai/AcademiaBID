interface BarData {
  label: string;
  values: { value: number; color: string; name: string }[];
}

interface BarChartProps {
  data: BarData[];
  height?: number;
}

export default function BarChart({ data, height = 200 }: BarChartProps) {
  const maxTotal = Math.max(...data.map(d => d.values.reduce((s, v) => s + v.value, 0)));

  return (
    <div className="w-full">
      <div className="flex items-end gap-3" style={{ height }}>
        {data.map((bar, i) => {
          const total = bar.values.reduce((s, v) => s + v.value, 0);
          return (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div className="w-full flex flex-col-reverse rounded-t-md overflow-hidden" style={{ height: `${(total / maxTotal) * (height - 24)}px` }}>
                {bar.values.map((v, j) => (
                  <div
                    key={j}
                    className="w-full transition-all duration-500"
                    style={{
                      height: `${(v.value / total) * 100}%`,
                      background: v.color,
                      minHeight: v.value > 0 ? '2px' : '0',
                    }}
                    title={`${v.name}: ${v.value}h`}
                  />
                ))}
              </div>
              <span className="text-xs text-gray-500 whitespace-nowrap">{bar.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
