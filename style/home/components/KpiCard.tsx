interface KpiCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
  iconBg: string;
  iconColor: string;
  trend?: number;
  sparkData?: number[];
  sparkColor?: string;
}

export default function KpiCard({ title, value, subtitle, icon, iconBg, iconColor, trend, sparkData, sparkColor = '#51b1db' }: KpiCardProps) {
  const maxVal = sparkData ? Math.max(...sparkData) : 1;

  return (
    <div className="bg-white rounded-xl p-5 card-hover" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
      <div className="flex items-start justify-between mb-4">
        <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: iconBg }}>
          <i className={`${icon} text-xl`} style={{ color: iconColor }}></i>
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${trend >= 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500'}`}>
            <i className={`${trend >= 0 ? 'ri-arrow-up-line' : 'ri-arrow-down-line'} text-xs`}></i>
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-gray-800 mb-0.5">{value}</div>
      <div className="text-xs font-medium text-gray-500 mb-3">{title}</div>
      <div className="text-xs text-gray-400">{subtitle}</div>
      {sparkData && (
        <div className="flex items-end gap-0.5 mt-3 h-8">
          {sparkData.map((v, i) => (
            <div
              key={i}
              className="flex-1 rounded-sm transition-all"
              style={{
                height: `${(v / maxVal) * 100}%`,
                background: sparkColor,
                opacity: i === sparkData.length - 1 ? 1 : 0.4 + (i / sparkData.length) * 0.4,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
