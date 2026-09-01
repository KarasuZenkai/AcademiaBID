import { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import { weeklyHoursData, monthlyHoursTrend } from '@/mocks/activityData';

type ViewMode = 'weekly' | 'monthly';

interface CustomTooltipProps {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white rounded-xl border border-gray-100 px-4 py-3" style={{ boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}>
      <p className="text-xs font-bold text-gray-700 mb-2">{label}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2 mb-1">
          <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: p.color }} />
          <span className="text-xs text-gray-500">{p.name}:</span>
          <span className="text-xs font-bold text-gray-800">{p.value}h</span>
        </div>
      ))}
      {payload.length === 2 && (
        <div className="mt-2 pt-2 border-t border-gray-100">
          <span className="text-xs text-gray-400">
            Diferencia: <span className="font-bold text-orange-500">+{(payload[0].value - payload[1].value).toFixed(1)}h</span>
          </span>
        </div>
      )}
    </div>
  );
}

export default function WeeklyHoursChart() {
  const [view, setView] = useState<ViewMode>('weekly');

  const data = view === 'weekly' ? weeklyHoursData : monthlyHoursTrend;
  const xKey = view === 'weekly' ? 'date' : 'week';

  return (
    <div className="bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-5 flex-wrap gap-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">Horas Trabajadas</h3>
          <p className="text-xs text-gray-400 mt-0.5">Biométrico vs Tiempo Registrado</p>
        </div>
        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
            {(['weekly', 'monthly'] as ViewMode[]).map(v => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium cursor-pointer transition-all whitespace-nowrap ${
                  view === v ? 'bg-white text-gray-800' : 'text-gray-500 hover:text-gray-700'
                }`}
                style={view === v ? { boxShadow: '0 1px 4px rgba(0,0,0,0.1)' } : {}}
              >
                {v === 'weekly' ? 'Esta semana' : 'Este mes'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary pills */}
      <div className="flex gap-3 mb-4 flex-wrap">
        {[
          { label: 'Biométrico', value: view === 'weekly' ? '501.3h' : '1,276h', color: '#004a7c', bg: '#e3f2fd' },
          { label: 'Registrado', value: view === 'weekly' ? '452.2h' : '1,169h', color: '#28a745', bg: '#e8f5e9' },
          { label: 'Diferencia', value: view === 'weekly' ? '+49.1h' : '+107h', color: '#ff8f15', bg: '#fff3e0' },
        ].filter(Boolean).map(item => (
          <div key={item!.label} className="flex items-center gap-2 px-3 py-1.5 rounded-full" style={{ background: item!.bg }}>
            <div className="w-2 h-2 rounded-full" style={{ background: item!.color }} />
            <span className="text-xs text-gray-600">{item!.label}:</span>
            <span className="text-xs font-bold" style={{ color: item!.color }}>{item!.value}</span>
          </div>
        ))}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="gradBio" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#004a7c" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#004a7c" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradReg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#28a745" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#28a745" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradTarget" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff8f15" stopOpacity={0.08} />
              <stop offset="95%" stopColor="#ff8f15" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 11, fill: '#9ca3af' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#9ca3af' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={v => `${v}h`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: '11px', paddingTop: '12px' }}
          />
          {view === 'monthly' && (
            <ReferenceLine
              y={320}
              stroke="#ff8f15"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{ value: 'Meta', position: 'right', fontSize: 10, fill: '#ff8f15' }}
            />
          )}
          <Area
            type="monotone"
            dataKey="bio"
            name="Biométrico"
            stroke="#004a7c"
            strokeWidth={2.5}
            fill="url(#gradBio)"
            dot={{ fill: '#004a7c', r: 4, strokeWidth: 0 }}
            activeDot={{ r: 6, fill: '#004a7c', strokeWidth: 2, stroke: '#fff' }}
          />
          <Area
            type="monotone"
            dataKey="registered"
            name="Registrado"
            stroke="#28a745"
            strokeWidth={2.5}
            fill="url(#gradReg)"
            dot={{ fill: '#28a745', r: 4, strokeWidth: 0 }}
            activeDot={{ r: 6, fill: '#28a745', strokeWidth: 2, stroke: '#fff' }}
          />
          {view === 'monthly' && (
            <Area
              type="monotone"
              dataKey="target"
              name="Meta"
              stroke="#ff8f15"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              fill="url(#gradTarget)"
              dot={false}
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
