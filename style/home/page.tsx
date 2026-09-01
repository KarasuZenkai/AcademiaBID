import MainLayout from '@/components/feature/MainLayout';
import KpiCard from './components/KpiCard';
import WeeklyHoursChart from './components/WeeklyHoursChart';
import ProductivityChart from './components/ProductivityChart';
import { employees, attendanceRecords } from '@/mocks/employees';
import { tasks } from '@/mocks/tasks';
import { timeRecords } from '@/mocks/timeRecords';
import { employeeProductivity } from '@/mocks/activityData';
import { useRole } from '@/contexts/RoleContext';
import AvatarPhoto from '@/components/base/AvatarPhoto';

const totalHorasBio = attendanceRecords.reduce((s, r) => s + r.biometricHours, 0);
const totalHorasReg = timeRecords.reduce((s, r) => s + r.duration, 0);
const tareasCompletadas = tasks.filter(t => t.status === 'done').length;
const activeEmployees = employees.filter(e => e.status === 'active').length;

const avgProductivity = Math.round(
  employeeProductivity.reduce((s, e) => s + e.productive, 0) / employeeProductivity.length
);

// Usuario-specific data (mocked as Ana García — id 2)
const USER_EMPLOYEE_ID = 2;
const userEmployee = employees.find(e => e.id === USER_EMPLOYEE_ID)!;
const userTasks = tasks.filter(t => t.assignee === userEmployee.name);
const userTimeRecords = timeRecords.filter(r => r.employee === userEmployee.name);
const userProductivity = employeeProductivity.find(e => e.name === userEmployee.name);
const userBioHours = attendanceRecords.filter(r => r.employeeId === USER_EMPLOYEE_ID).reduce((s, r) => s + r.biometricHours, 0);
const userRegHours = userTimeRecords.reduce((s, r) => s + r.duration, 0);

export default function DashboardPage() {
  const { isUsuario, canSeeGlobal, displayName } = useRole();

  return (
    <MainLayout title="Dashboard Ejecutivo">
      {/* Header */}
      <div className="rounded-2xl p-6 mb-6 text-white relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #002952 0%, #004a7c 60%, #005a94 100%)' }}>
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 80% 50%, #51b1db 0%, transparent 60%)' }} />
        <div className="relative z-10 flex items-center justify-between flex-wrap gap-4">
          <div>
            <div className="inline-flex items-center gap-2 bg-white/10 rounded-full px-3 py-1 text-xs text-cyan-300 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block"></span>
              En Tiempo Real
            </div>
            <h2 className="text-2xl font-bold mb-1">
              {isUsuario ? `Hola, ${displayName.name.split(' ')[0]}` : 'Resumen de Productividad'}
            </h2>
            <p className="text-white/70 text-sm">
              {isUsuario
                ? `Tu resumen semanal del 6 al 12 de Abril, 2026`
                : `Semana del 6 al 12 de Abril, 2026 · ${activeEmployees} empleados activos`}
            </p>
          </div>
          <div className="flex gap-3">
            {canSeeGlobal && (
              <button className="flex items-center gap-2 bg-white/10 hover:bg-white/20 transition-colors rounded-lg px-4 py-2 text-sm font-medium cursor-pointer whitespace-nowrap">
                <i className="ri-download-line"></i> Exportar Reporte
              </button>
            )}
            <button className="flex items-center gap-2 bg-white text-[#004a7c] hover:bg-white/90 transition-colors rounded-lg px-4 py-2 text-sm font-bold cursor-pointer whitespace-nowrap">
              <i className="ri-refresh-line"></i> Actualizar
            </button>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {isUsuario ? (
          <>
            <KpiCard
              title="Mis Horas"
              value={`${userRegHours.toFixed(1)}h`}
              subtitle="Registradas esta semana"
              icon="ri-time-line"
              iconBg="#e8f5e9"
              iconColor="#28a745"
              trend={4}
              sparkData={[6, 7, 8, 6, 9, 7, 8]}
              sparkColor="#28a745"
            />
            <KpiCard
              title="Mi Productividad"
              value={`${userProductivity?.productive ?? 0}%`}
              subtitle="Actividad productiva"
              icon="ri-bar-chart-grouped-line"
              iconBg="#e3f2fd"
              iconColor="#0e8aaf"
              trend={2}
              sparkData={[78, 80, 79, 82, 83, 85, 85]}
              sparkColor="#0e8aaf"
            />
            <KpiCard
              title="Mis Tareas"
              value={`${userTasks.filter(t => t.status === 'done').length}/${userTasks.length}`}
              subtitle="Completadas esta semana"
              icon="ri-checkbox-circle-line"
              iconBg="#fce4ec"
              iconColor="#c60b44"
              trend={-1}
              sparkData={[2, 3, 1, 4, 3, 5, 2]}
              sparkColor="#c60b44"
            />
            <KpiCard
              title="Tiempo Improductivo"
              value={`${userProductivity?.unproductive ?? 0}%`}
              subtitle="Tu promedio hoy"
              icon="ri-alarm-warning-line"
              iconBg="#fff3e0"
              iconColor="#ff8f15"
              trend={-3}
              sparkData={[15, 12, 11, 10, 8, 10, 8]}
              sparkColor="#ff8f15"
            />
          </>
        ) : (
          <>
            <KpiCard
              title="Horas Trabajadas"
              value={`${totalHorasBio.toFixed(1)}h`}
              subtitle="Registro biométrico hoy"
              icon="ri-time-line"
              iconBg="#e8f5e9"
              iconColor="#28a745"
              trend={4}
              sparkData={[62, 68, 71, 65, 74, 70, 73]}
              sparkColor="#28a745"
            />
            <KpiCard
              title="Productividad Promedio"
              value={`${avgProductivity}%`}
              subtitle="Actividad productiva del equipo"
              icon="ri-bar-chart-grouped-line"
              iconBg="#e3f2fd"
              iconColor="#0e8aaf"
              trend={2}
              sparkData={[80, 82, 79, 85, 83, 87, 85]}
              sparkColor="#0e8aaf"
            />
            <KpiCard
              title="Tareas Completadas"
              value={`${tareasCompletadas}/${tasks.length}`}
              subtitle="Esta semana"
              icon="ri-checkbox-circle-line"
              iconBg="#fce4ec"
              iconColor="#c60b44"
              trend={-1}
              sparkData={[3, 5, 4, 6, 5, 7, 2]}
              sparkColor="#c60b44"
            />
            <KpiCard
              title="Tiempo Improductivo"
              value="8.2%"
              subtitle="Promedio del equipo hoy"
              icon="ri-alarm-warning-line"
              iconBg="#fff3e0"
              iconColor="#ff8f15"
              trend={-3}
              sparkData={[12, 10, 11, 9, 8, 10, 8]}
              sparkColor="#ff8f15"
            />
          </>
        )}
      </div>

      {/* Charts Row — Recharts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <WeeklyHoursChart />
        <ProductivityChart />
      </div>

      {/* Activity donut + Top employees */}
      {canSeeGlobal ? (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-6">
          {/* Donut */}
          <div className="lg:col-span-2 bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Actividad Global</h3>
            <div className="flex items-center gap-4">
              <div className="relative w-24 h-24 flex-shrink-0">
                <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f0f0f0" strokeWidth="3" />
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#28a745" strokeWidth="3" strokeDasharray="85 15" strokeLinecap="round" />
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#51b1db" strokeWidth="3" strokeDasharray="10 90" strokeDashoffset="-85" strokeLinecap="round" />
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#ff8f15" strokeWidth="3" strokeDasharray="5 95" strokeDashoffset="-95" strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-lg font-bold text-gray-800">85%</span>
                  <span className="text-xs text-gray-400">prod.</span>
                </div>
              </div>
              <div className="space-y-2 flex-1">
                {[
                  { label: 'Productivo', pct: 85, color: '#28a745' },
                  { label: 'Neutral', pct: 10, color: '#51b1db' },
                  { label: 'Improductivo', pct: 5, color: '#ff8f15' },
                ].map(item => (
                  <div key={item.label}>
                    <div className="flex justify-between text-xs mb-0.5">
                      <span className="text-gray-600">{item.label}</span>
                      <span className="font-semibold text-gray-700">{item.pct}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full">
                      <div className="h-full rounded-full" style={{ width: `${item.pct}%`, background: item.color }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top employees */}
          <div className="lg:col-span-3 bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h3 className="text-sm font-semibold text-gray-800 mb-3">Ranking de Productividad</h3>
            <div className="space-y-2.5">
              {[...employeeProductivity].sort((a, b) => b.productive - a.productive).map((emp, i) => (
                <div key={emp.name} className="flex items-center gap-3">
                  <span className={`text-xs font-bold w-5 text-center ${i === 0 ? 'text-yellow-500' : i === 1 ? 'text-gray-400' : i === 2 ? 'text-orange-400' : 'text-gray-300'}`}>
                    {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}`}
                  </span>
                  <AvatarPhoto
                    name={emp.name}
                    size={28}
                    gradientFallback="linear-gradient(135deg, #004a7c, #0e8aaf)"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between mb-0.5">
                      <p className="text-xs font-medium text-gray-700 truncate">{emp.name}</p>
                      <span className="text-xs font-bold ml-2 flex-shrink-0" style={{ color: emp.productive >= 90 ? '#28a745' : emp.productive >= 80 ? '#004a7c' : '#ff8f15' }}>
                        {emp.productive}%
                      </span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                          width: `${emp.productive}%`,
                          background: emp.productive >= 90 ? '#28a745' : emp.productive >= 80 ? 'linear-gradient(90deg,#004a7c,#51b1db)' : '#ff8f15',
                        }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 w-10 text-right flex-shrink-0">{emp.activeHours}h</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* Usuario view: personal stats */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          <div className="lg:col-span-1 bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Tu Actividad</h3>
            <div className="flex items-center gap-4">
              <div className="relative w-24 h-24 flex-shrink-0">
                <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f0f0f0" strokeWidth="3" />
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#28a745" strokeWidth="3" strokeDasharray={`${userProductivity?.productive ?? 0} ${100 - (userProductivity?.productive ?? 0)}`} strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-lg font-bold text-gray-800">{userProductivity?.productive ?? 0}%</span>
                  <span className="text-xs text-gray-400">prod.</span>
                </div>
              </div>
              <div className="space-y-2 flex-1">
                {[
                  { label: 'Productivo', pct: userProductivity?.productive ?? 0, color: '#28a745' },
                  { label: 'Neutral', pct: userProductivity?.neutral ?? 0, color: '#51b1db' },
                  { label: 'Improductivo', pct: userProductivity?.unproductive ?? 0, color: '#ff8f15' },
                ].map(item => (
                  <div key={item.label}>
                    <div className="flex justify-between text-xs mb-0.5">
                      <span className="text-gray-600">{item.label}</span>
                      <span className="font-semibold text-gray-700">{item.pct}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full">
                      <div className="h-full rounded-full" style={{ width: `${item.pct}%`, background: item.color }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2 bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h3 className="text-sm font-semibold text-gray-800 mb-3">Tu Rendimiento</h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              {[
                { label: 'Horas Biométricas', value: `${userBioHours.toFixed(1)}h`, color: '#004a7c' },
                { label: 'Horas Registradas', value: `${userRegHours.toFixed(1)}h`, color: '#28a745' },
                { label: 'Diferencia', value: `${(userBioHours - userRegHours).toFixed(1)}h`, color: userBioHours - userRegHours > 1 ? '#ff8f15' : '#28a745' },
              ].map(s => (
                <div key={s.label} className="text-center p-3 rounded-lg" style={{ background: `${s.color}10` }}>
                  <div className="text-lg font-bold" style={{ color: s.color }}>{s.value}</div>
                  <div className="text-xs text-gray-500">{s.label}</div>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              {[
                { label: 'Puntualidad', value: 95, color: '#28a745' },
                { label: 'Cumplimiento de tareas', value: Math.round((userTasks.filter(t => t.status === 'done').length / (userTasks.length || 1)) * 100), color: '#004a7c' },
                { label: 'Eficiencia', value: 87, color: '#0e8aaf' },
              ].map(item => (
                <div key={item.label}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">{item.label}</span>
                    <span className="font-semibold text-gray-700">{item.value}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full">
                    <div className="h-full rounded-full transition-all duration-700" style={{ width: `${item.value}%`, background: item.color }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent tasks */}
        <div className="lg:col-span-2 bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-800">
              {isUsuario ? 'Mis Tareas Recientes' : 'Tareas Recientes'}
            </h3>
            <a href="/tareas" className="text-xs text-[#004a7c] hover:underline cursor-pointer">Ver todas</a>
          </div>
          <div className="space-y-2">
            {(isUsuario ? userTasks : tasks).slice(0, 5).map(task => {
              const statusMap: Record<string, { label: string; color: string; bg: string }> = {
                pending: { label: 'Pendiente', color: '#ff8f15', bg: '#fff3e0' },
                in_progress: { label: 'En Proceso', color: '#0e8aaf', bg: '#e3f2fd' },
                done: { label: 'Terminado', color: '#28a745', bg: '#e8f5e9' },
              };
              const priorityMap: Record<string, string> = { low: '#808080', medium: '#ff8f15', high: '#c60b44', critical: '#7d0000' };
              const s = statusMap[task.status];
              return (
                <div key={task.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: priorityMap[task.priority] }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-700 truncate">{task.title}</p>
                    <p className="text-xs text-gray-400">{task.project}</p>
                  </div>
                  <AvatarPhoto
                    name={task.assignee}
                    size={24}
                    gradientFallback="linear-gradient(135deg, #004a7c, #0e8aaf)"
                  />
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap" style={{ color: s.color, background: s.bg }}>
                    {s.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Attendance summary */}
        {canSeeGlobal ? (
          <div className="bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Asistencia Hoy</h3>
            <div className="grid grid-cols-2 gap-3 mb-4">
              {[
                { label: 'Presentes', value: activeEmployees, color: '#28a745', icon: 'ri-user-follow-line' },
                { label: 'Ausentes', value: employees.length - activeEmployees, color: '#c60b44', icon: 'ri-user-unfollow-line' },
                { label: 'Vacaciones', value: employees.filter(e => e.status === 'vacation').length, color: '#0e8aaf', icon: 'ri-sun-line' },
                { label: 'Total', value: employees.length, color: '#004a7c', icon: 'ri-team-line' },
              ].map(item => (
                <div key={item.label} className="rounded-lg p-3 text-center" style={{ background: `${item.color}10` }}>
                  <div className="w-6 h-6 flex items-center justify-center mx-auto mb-1">
                    <i className={`${item.icon} text-base`} style={{ color: item.color }}></i>
                  </div>
                  <div className="text-lg font-bold" style={{ color: item.color }}>{item.value}</div>
                  <div className="text-xs text-gray-500">{item.label}</div>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              {attendanceRecords.slice(0, 4).map(rec => {
                const emp = employees.find(e => e.id === rec.employeeId);
                const diff = rec.biometricHours - rec.registeredHours;
                return (
                  <div key={rec.employeeId} className="flex items-center gap-2">
                    <AvatarPhoto
                      name={emp?.name || ''}
                      size={24}
                      gradientFallback="linear-gradient(135deg, #004a7c, #0e8aaf)"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-700 truncate">{emp?.name}</p>
                    </div>
                    <span className={`text-xs font-semibold ${diff > 1 ? 'text-red-500' : 'text-green-600'}`}>
                      {diff > 0 ? '+' : ''}{diff.toFixed(1)}h
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* Usuario: quick links */
          <div className="bg-white rounded-xl p-5" style={{ boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Accesos Rápidos</h3>
            <div className="space-y-2">
              {[
                { label: 'Registrar Tiempo', icon: 'ri-timer-line', path: '/tiempo', color: '#004a7c', bg: '#e3f2fd' },
                { label: 'Mis Tareas', icon: 'ri-task-line', path: '/tareas', color: '#ff8f15', bg: '#fff3e0' },
                { label: 'Mi Actividad', icon: 'ri-bar-chart-grouped-line', path: '/actividad', color: '#28a745', bg: '#e8f5e9' },
                { label: 'Chat Interno', icon: 'ri-message-3-line', path: '/chat', color: '#0e8aaf', bg: '#e3f2fd' },
              ].map(link => (
                <a key={link.label} href={link.path} className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: link.bg }}>
                    <i className={`${link.icon} text-sm`} style={{ color: link.color }}></i>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-700">{link.label}</p>
                  </div>
                  <i className="ri-arrow-right-s-line text-gray-300 ml-auto text-sm"></i>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}