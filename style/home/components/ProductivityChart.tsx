import { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  Legend,
} from 'recharts';
import { employeeProductivity, employeeWeeklyHours } from '@/mocks/activityData';

type ChartMode = 'bar' | 'radar';

interface BarTooltipProps {
  active?: boolean;
  payload?: { value: number; payload: { name: string; productive: number; neutral: number; unproductive: number; activeHours: number } }[];
  label?: string;
}

function BarTooltip({ active, payload, label }: BarTooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-xl border border-gray-100 px-4 py-3" style={{ boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}>
      <p className="text-xs font-bold text-gray-700 mb-2">{label}</p>
      <div className="space-y-1.5">
        {[
          { label: 'Productivo', value: d.productive, color: '#28a745' },
          { label: 'Neutral', value: d.neutral, color: '#51b1db' },
          { label: 'Improductivo', value: d.unproductive, color: '#ff8f15' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full" style={{ background: item.color }} />
            <span className="text-xs text-gray-500">{item.label}:</span>
            <span className="text-xs font-bold" style={{ color: item.color }}>{item.value}%</span>
          </div>
        ))}
        <div className="pt-1.5 border-t border-gray-100 mt-1">
          <span className="text-xs text-gray-400">Horas activas: <span className="font-bold text-gray-700">{d.activeHours}h</span></span>
        </div>
      </div>
    </div>
  );
}

interface HoursTooltipProps {
  active?: boolean;
  payload?: { value: number; payload: { name: string; hours: number; target: number; productive: number } }[];
  label?: string;
}

function HoursTooltip({ active, payload, label }: HoursTooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  const pct = Math.round((d.hours / d.target) * 100);
  return (
    <div className="bg-white rounded-xl border border-gray-100 px-4 py-3" style={{ boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}>
      <p className="text-xs font-bold text-gray-700 mb-2">{label}</p>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#004a7c]" />
          <span className="text-xs text-gray-500">Horas:</span>
          <span className="text-xs font-bold text-[#004a7c]">{d.hours}h / {d.target}h</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-xs text-gray-500">Cumplimiento:</span>
          <span className={`text-xs font-bold ${pct >= 100 ? 'text-green-600' : pct >= 80 ? 'text-orange-500' : 'text-red-500'}`}>{pct}%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#51b1db]" />
          <span className="text-xs text-gray-500">Productividad:</span>
          <span className="text-xs font-bold text-[#0e8aaf]">{d.productive}%</span>
        </div>
      </div>
    </div>
  );
}

const radarData = employeeProductivity.map(e => ({
  subject: e.name.split(' ')[0],
  Productivo: e.productive,
  Neutral: e.neutral,
  Improductivo: e.unproductive,
}));

export default function ProductivityChart() {
  const [mode, setMode] = useState<ChartMode>('bar');
  const [metric, setMetric] = useState<'productivity' | 'hours'>('productivity');

  return (
    <div className="bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">Comparativa por Empleado</h3>
          <p className="text-xs text-gray-400 mt-0.5">Productividad y horas esta semana</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Metric toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
            {([
              { key: 'productivity', label: 'Productividad' },
              { key: 'hours', label: 'Horas' },
            ] as { key: 'productivity' | 'hours'; label: string }[]).map(m => (
              <button
                key={m.key}
                onClick={() => setMetric(m.key)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium cursor-pointer transition-all whitespace-nowrap ${
                  metric === m.key ? 'bg-white text-gray-800' : 'text-gray-500 hover:text-gray-700'
                }`}
                style={metric === m.key ? { boxShadow: '0 1px 4px rgba(0,0,0,0.1)' } : {}}
              >
                {m.label}
              </button>
            ))}
          </div>
          {/* Chart type toggle */}
          <div className="flex items-center gap-1">
            {([
              { key: 'bar', icon: 'ri-bar-chart-2-line' },
              { key: 'radar', icon: 'ri-radar-line' },
            ] as { key: ChartMode; icon: string }[]).map(t => (
              <button
                key={t.key}
                onClick={() => setMode(t.key)}
                className={`w-7 h-7 flex items-center justify-center rounded-lg cursor-pointer transition-all ${
                  mode === t.key ? 'text-white' : 'text-gray-400 hover:bg-gray-100'
                }`}
                style={mode === t.key ? { background: 'linear-gradient(135deg,#004a7c,#005a94)' } : {}}
              >
                <i className={`${t.icon} text-sm`}></i>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      {mode === 'bar' ? (
        metric === 'productivity' ? (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={employeeProductivity} margin={{ top: 5, right: 10, left: -20, bottom: 0 }} barSize={28}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis
                dataKey="name"
                tickFormatter={v => v.split(' ')[0]}
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                axisLine={false}
                tickLine={false}
                tickFormatter={v => `${v}%`}
                domain={[0, 100]}
              />
              <Tooltip content={<BarTooltip />} cursor={{ fill: 'rgba(0,74,124,0.04)', radius: 6 }} />
              <Bar dataKey="productive" name="Productivo" radius={[6, 6, 0, 0]}>
                {employeeProductivity.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.productive >= 90 ? '#28a745' : entry.productive >= 80 ? '#004a7c' : entry.productive >= 70 ? '#ff8f15' : '#c60b44'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={employeeWeeklyHours} margin={{ top: 5, right: 10, left: -20, bottom: 0 }} barSize={20} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#9ca3af' }}
                axisLine={false}
                tickLine={false}
                tickFormatter={v => `${v}h`}
                domain={[0, 50]}
              />
              <Tooltip content={<HoursTooltip />} cursor={{ fill: 'rgba(0,74,124,0.04)', radius: 6 }} />
              <Legend
                iconType="circle"
                iconSize={8}
                wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
              />
              <Bar dataKey="target" name="Meta" fill="#e5e5e5" radius={[4, 4, 0, 0]} />
              <Bar dataKey="hours" name="Horas reales" radius={[4, 4, 0, 0]}>
                {employeeWeeklyHours.map((entry, index) => (
                  <Cell
                    key={`cell-h-${index}`}
                    fill={entry.hours >= entry.target ? '#28a745' : entry.hours >= entry.target * 0.8 ? '#004a7c' : '#ff8f15'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <RadarChart data={radarData} margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
            <PolarGrid stroke="#f0f0f0" />
            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#6b7280' }} />
            <Radar name="Productivo" dataKey="Productivo" stroke="#28a745" fill="#28a745" fillOpacity={0.15} strokeWidth={2} />
            <Radar name="Neutral" dataKey="Neutral" stroke="#51b1db" fill="#51b1db" fillOpacity={0.1} strokeWidth={2} />
            <Radar name="Improductivo" dataKey="Improductivo" stroke="#ff8f15" fill="#ff8f15" fillOpacity={0.1} strokeWidth={2} />
            <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
            <Tooltip
              contentStyle={{ borderRadius: '12px', border: '1px solid #f0f0f0', fontSize: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}
              formatter={(value: number, name: string) => [`${value}%`, name]}
            />
          </RadarChart>
        </ResponsiveContainer>
      )}

      {/* Bottom legend / insight */}
      <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-3 gap-3">
        {[
          { label: 'Mejor rendimiento', value: 'Roberto S.', sub: '95% productivo', color: '#28a745', icon: 'ri-trophy-line' },
          { label: 'Promedio equipo', value: `${Math.round(employeeProductivity.reduce((s, e) => s + e.productive, 0) / employeeProductivity.length)}%`, sub: 'productividad', color: '#004a7c', icon: 'ri-team-line' },
          { label: 'Requiere atención', value: 'María L.', sub: '72% productivo', color: '#ff8f15', icon: 'ri-alert-line' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-2 p-2.5 rounded-lg" style={{ background: `${item.color}08` }}>
            <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${item.color}18` }}>
              <i className={`${item.icon} text-sm`} style={{ color: item.color }}></i>
            </div>
            <div className="min-w-0">
              <p className="text-xs text-gray-400 truncate">{item.label}</p>
              <p className="text-xs font-bold truncate" style={{ color: item.color }}>{item.value}</p>
              <p className="text-xs text-gray-400 truncate">{item.sub}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
